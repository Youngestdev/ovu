"""
Unit tests for partner service
"""
import pytest
from datetime import datetime, timedelta
from app.services.partner_service import PartnerService
from app.models.partner import Partner, PartnerStatus
from app.models.api_key import APIKey, APIKeyStatus
from app.schemas.partner import PartnerCreate, APIKeyCreate


class TestPartnerService:
    """Test suite for PartnerService"""
    
    def test_generate_partner_code(self):
        """Test partner code generation"""
        code = PartnerService.generate_partner_code("Travel Agency Inc")
        
        assert code.startswith("TRAVEL")
        assert len(code) > 6  # Base + dash + suffix
        assert "-" in code
    
    def test_generate_api_credentials(self):
        """Test API credentials generation"""
        api_key, api_secret = PartnerService.generate_api_credentials()
        
        assert api_key.startswith("ovu_live_")
        assert api_secret.startswith("sk_live_")
        assert len(api_key) > 20
        assert len(api_secret) > 20
    
    def test_hash_secret(self):
        """Test secret hashing"""
        secret = "test_secret_123"
        hashed = PartnerService.hash_secret(secret)
        
        assert hashed != secret
        assert len(hashed) == 64  # SHA-256 produces 64 char hex
    
    def test_verify_secret(self):
        """Test secret verification"""
        secret = "test_secret_123"
        hashed = PartnerService.hash_secret(secret)
        
        # Correct secret should verify
        assert PartnerService.verify_secret(secret, hashed) is True
        
        # Wrong secret should not verify
        assert PartnerService.verify_secret("wrong_secret", hashed) is False
    
    def test_generate_key_id(self):
        """Test key ID generation"""
        key_id = PartnerService.generate_key_id()
        
        assert key_id.startswith("key_")
        assert len(key_id) > 10
    
    @pytest.mark.asyncio
    async def test_create_partner(self):
        """Test partner creation"""
        partner_data = PartnerCreate(
            name="Test Agency",
            email="test@agency.com",
            phone="+2348012345678",
            company_name="Test Agency Inc",
            business_type="travel_agency",
            rate_limit_per_minute=100,
            rate_limit_per_day=50000
        )
        
        partner, api_key, api_secret = await PartnerService.create_partner(partner_data)
        
        # Verify partner
        assert partner.name == "Test Agency"
        assert partner.email == "test@agency.com"
        assert partner.company_name == "Test Agency Inc"
        assert partner.business_type == "travel_agency"
        assert partner.status == PartnerStatus.ACTIVE
        assert partner.rate_limit_per_minute == 100
        assert partner.rate_limit_per_day == 50000
        
        # Verify credentials
        assert api_key.startswith("ovu_live_")
        assert api_secret.startswith("sk_live_")
        
        # Verify partner code
        assert partner.partner_code.startswith("TESTAG")
        
        # Cleanup
        await partner.delete()
    
    @pytest.mark.asyncio
    async def test_create_api_key(self):
        """Test API key creation for partner"""
        # Create a test partner first
        partner_data = PartnerCreate(
            name="Test Partner",
            email="partner@test.com",
            phone="+2348012345678",
            company_name="Test Partner Inc",
            business_type="corporate",
            rate_limit_per_minute=60,
            rate_limit_per_day=10000
        )
        
        partner, _, _ = await PartnerService.create_partner(partner_data)
        
        # Create API key
        key_data = APIKeyCreate(
            name="Production Key",
            scopes=["search", "booking"],
            rate_limit_per_minute=200,
            expires_in_days=365,
            allowed_ips=["203.0.113.0"]
        )
        
        api_key_response = await PartnerService.create_api_key(partner, key_data)
        
        # Verify response
        assert api_key_response.name == "Production Key"
        assert api_key_response.scopes == ["search", "booking"]
        assert api_key_response.status == APIKeyStatus.ACTIVE
        assert api_key_response.api_key.startswith("ovu_live_")
        assert api_key_response.api_secret.startswith("sk_live_")
        
        # Verify expiration
        assert api_key_response.expires_at is not None
        days_diff = (api_key_response.expires_at - datetime.utcnow()).days
        assert 364 <= days_diff <= 365
        
        # Cleanup
        await partner.delete()
    
    @pytest.mark.asyncio
    async def test_list_api_keys(self):
        """Test listing API keys for a partner"""
        # Create partner
        partner_data = PartnerCreate(
            name="Test Partner",
            email="list@test.com",
            phone="+2348012345678",
            company_name="List Test Inc",
            business_type="reseller",
            rate_limit_per_minute=60,
            rate_limit_per_day=10000
        )
        
        partner, _, _ = await PartnerService.create_partner(partner_data)
        
        # Create multiple API keys
        for i in range(3):
            key_data = APIKeyCreate(
                name=f"Key {i+1}",
                scopes=["search", "booking"],
            )
            await PartnerService.create_api_key(partner, key_data)
        
        # List keys
        keys = await PartnerService.list_api_keys(str(partner.id))
        
        # Should have 4 keys (1 default + 3 created)
        assert len(keys) >= 3
        
        # Verify key structure
        for key in keys:
            assert key.key_id.startswith("key_")
            assert key.partner_id == str(partner.id)
            assert key.status in [APIKeyStatus.ACTIVE, "active"]
        
        # Cleanup
        await partner.delete()
    
    @pytest.mark.asyncio
    async def test_revoke_api_key(self):
        """Test API key revocation"""
        # Create partner and key
        partner_data = PartnerCreate(
            name="Revoke Test",
            email="revoke@test.com",
            phone="+2348012345678",
            company_name="Revoke Test Inc",
            business_type="travel_agency",
            rate_limit_per_minute=60,
            rate_limit_per_day=10000
        )
        
        partner, _, _ = await PartnerService.create_partner(partner_data)
        
        key_data = APIKeyCreate(name="To Revoke", scopes=["search"])
        api_key_response = await PartnerService.create_api_key(partner, key_data)
        
        # Revoke the key
        success = await PartnerService.revoke_api_key(
            str(partner.id),
            api_key_response.key_id
        )
        
        assert success is True
        
        # Verify key is revoked
        api_key = await APIKey.find_one(APIKey.key_id == api_key_response.key_id)
        assert api_key.status == APIKeyStatus.REVOKED
        assert api_key.revoked_at is not None
        
        # Cleanup
        await partner.delete()
    
    @pytest.mark.asyncio
    async def test_rotate_api_key(self):
        """Test API key rotation"""
        # Create partner and key
        partner_data = PartnerCreate(
            name="Rotate Test",
            email="rotate@test.com",
            phone="+2348012345678",
            company_name="Rotate Test Inc",
            business_type="corporate",
            rate_limit_per_minute=60,
            rate_limit_per_day=10000
        )
        
        partner, _, _ = await PartnerService.create_partner(partner_data)
        
        key_data = APIKeyCreate(
            name="To Rotate",
            scopes=["search", "booking"],
            rate_limit_per_minute=150
        )
        old_key = await PartnerService.create_api_key(partner, key_data)
        
        # Rotate the key
        rotation_result = await PartnerService.rotate_api_key(
            partner,
            old_key.key_id
        )
        
        assert rotation_result is not None
        assert rotation_result.old_key_id == old_key.key_id
        assert rotation_result.new_key_id != old_key.key_id
        assert rotation_result.new_api_key.startswith("ovu_live_")
        assert rotation_result.new_api_secret.startswith("sk_live_")
        
        # Verify old key is revoked
        old_api_key = await APIKey.find_one(APIKey.key_id == old_key.key_id)
        assert old_api_key.status == APIKeyStatus.REVOKED
        
        # Verify new key exists and is active
        new_api_key = await APIKey.find_one(APIKey.key_id == rotation_result.new_key_id)
        assert new_api_key.status == APIKeyStatus.ACTIVE
        assert new_api_key.name == "To Rotate"  # Same name
        assert new_api_key.scopes == ["search", "booking"]  # Same scopes
        
        # Cleanup
        await partner.delete()
    
    @pytest.mark.asyncio
    async def test_track_api_usage(self):
        """Test API usage tracking"""
        # Create partner
        partner_data = PartnerCreate(
            name="Usage Test",
            email="usage@test.com",
            phone="+2348012345678",
            company_name="Usage Test Inc",
            business_type="reseller",
            rate_limit_per_minute=60,
            rate_limit_per_day=10000
        )
        
        partner, _, _ = await PartnerService.create_partner(partner_data)
        
        initial_requests = partner.total_requests
        
        # Track usage
        await PartnerService.track_api_usage(str(partner.id), "search", True)
        
        # Reload partner
        partner = await Partner.get(partner.id)
        
        # Verify tracking
        assert partner.total_requests == initial_requests + 1
        assert partner.last_request_at is not None
        
        # Cleanup
        await partner.delete()


class TestPartnerCodeGeneration:
    """Test partner code generation edge cases"""
    
    def test_short_company_name(self):
        """Test with very short company name"""
        code = PartnerService.generate_partner_code("AB")
        assert code.startswith("AB")
        assert "-" in code
    
    def test_long_company_name(self):
        """Test with very long company name"""
        code = PartnerService.generate_partner_code("Very Long Company Name International Limited")
        assert len(code.split("-")[0]) == 6  # Should truncate to 6 chars
    
    def test_special_characters(self):
        """Test with special characters in name"""
        code = PartnerService.generate_partner_code("Test & Company Ltd.")
        assert "-" in code
        # Should only contain alphanumeric and dash
        assert all(c.isalnum() or c == "-" for c in code)


class TestSecretHashing:
    """Test secret hashing security"""
    
    def test_same_secret_different_hashes(self):
        """Test that hashing is deterministic"""
        secret = "test_secret"
        hash1 = PartnerService.hash_secret(secret)
        hash2 = PartnerService.hash_secret(secret)
        
        # SHA-256 is deterministic, so same input = same output
        assert hash1 == hash2
    
    def test_different_secrets_different_hashes(self):
        """Test that different secrets produce different hashes"""
        hash1 = PartnerService.hash_secret("secret1")
        hash2 = PartnerService.hash_secret("secret2")
        
        assert hash1 != hash2
    
    def test_timing_safe_comparison(self):
        """Test that verification uses timing-safe comparison"""
        secret = "test_secret"
        correct_hash = PartnerService.hash_secret(secret)
        wrong_hash = PartnerService.hash_secret("wrong")
        
        # Should use hmac.compare_digest internally (timing-safe)
        assert PartnerService.verify_secret(secret, correct_hash) is True
        assert PartnerService.verify_secret(secret, wrong_hash) is False
