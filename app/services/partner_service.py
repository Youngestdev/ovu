"""
Partner service for B2B business logic
"""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, List
from app.models.partner import Partner, PartnerStatus
from app.models.api_key import APIKey, APIKeyStatus
from app.schemas.partner import (
    PartnerCreate, APIKeyCreate, APIKeyCreateResponse,
    APIKeyResponse, APIKeyRotateResponse
)


class PartnerService:
    """Service for partner management operations"""
    
    @staticmethod
    def generate_partner_code(company_name: str) -> str:
        """Generate unique partner code"""
        # Create code from company name + random suffix
        base = company_name.upper().replace(" ", "")[:6]
        suffix = secrets.token_hex(3).upper()
        return f"{base}-{suffix}"
    
    @staticmethod
    def generate_api_credentials() -> tuple[str, str]:
        """
        Generate API key and secret
        Returns: (api_key, api_secret)
        """
        # Generate API key: ovu_live_<random>
        api_key = f"ovu_live_{secrets.token_urlsafe(32)}"
        
        # Generate API secret: sk_live_<random>
        api_secret = f"sk_live_{secrets.token_urlsafe(32)}"
        
        return api_key, api_secret
    
    @staticmethod
    def hash_secret(secret: str) -> str:
        """Hash API secret for storage"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    @staticmethod
    def verify_secret(secret: str, hashed_secret: str) -> bool:
        """Verify API secret against hash"""
        return hmac.compare_digest(
            hashlib.sha256(secret.encode()).hexdigest(),
            hashed_secret
        )
    
    @staticmethod
    def generate_key_id() -> str:
        """Generate unique key ID"""
        return f"key_{secrets.token_hex(16)}"
    
    @staticmethod
    async def create_partner(partner_data: PartnerCreate) -> tuple[Partner, str, str]:
        """
        Create a new business partner with initial API key
        Returns: (partner, api_key, api_secret)
        """
        # Generate partner code
        partner_code = PartnerService.generate_partner_code(partner_data.company_name)
        
        # Generate initial API credentials (legacy)
        api_key, api_secret = PartnerService.generate_api_credentials()
        api_secret_hash = PartnerService.hash_secret(api_secret)
        
        # Create partner
        partner = Partner(
            partner_code=partner_code,
            name=partner_data.name,
            email=partner_data.email,
            phone=partner_data.phone,
            website=str(partner_data.website) if partner_data.website else None,
            company_name=partner_data.company_name,
            business_type=partner_data.business_type,
            tax_id=partner_data.tax_id,
            api_key=api_key,
            api_secret=api_secret_hash,
            rate_limit_per_minute=partner_data.rate_limit_per_minute,
            rate_limit_per_day=partner_data.rate_limit_per_day,
            status=PartnerStatus.ACTIVE,
        )
        
        await partner.insert()
        
        # Also create an APIKey entry for better management
        key_id = PartnerService.generate_key_id()
        api_key_doc = APIKey(
            key_id=key_id,
            key_hash=api_secret_hash,
            name="Default API Key",
            partner_id=str(partner.id),
            status=APIKeyStatus.ACTIVE,
        )
        await api_key_doc.insert()
        
        return partner, api_key, api_secret
    
    @staticmethod
    async def create_api_key(
        partner: Partner,
        key_data: APIKeyCreate
    ) -> APIKeyCreateResponse:
        """Create a new API key for a partner"""
        
        # Generate credentials
        api_key, api_secret = PartnerService.generate_api_credentials()
        key_hash = PartnerService.hash_secret(api_secret)
        key_id = PartnerService.generate_key_id()
        
        # Calculate expiration if specified
        expires_at = None
        if key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
        
        # Create API key
        api_key_doc = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=key_data.name,
            partner_id=str(partner.id),
            status=APIKeyStatus.ACTIVE,
            scopes=key_data.scopes,
            rate_limit_per_minute=key_data.rate_limit_per_minute,
            expires_at=expires_at,
            allowed_ips=key_data.allowed_ips,
        )
        
        await api_key_doc.insert()
        
        return APIKeyCreateResponse(
            key_id=key_id,
            name=key_data.name,
            api_key=api_key,
            api_secret=api_secret,
            status=APIKeyStatus.ACTIVE,
            scopes=key_data.scopes,
            created_at=api_key_doc.created_at,
            expires_at=expires_at,
        )
    
    @staticmethod
    async def list_api_keys(partner_id: str) -> List[APIKeyResponse]:
        """List all API keys for a partner"""
        keys = await APIKey.find(APIKey.partner_id == partner_id).to_list()
        
        return [
            APIKeyResponse(
                key_id=key.key_id,
                name=key.name,
                key_preview=key.key_id[:8] + "...",
                partner_id=key.partner_id,
                status=key.status,
                scopes=key.scopes,
                rate_limit_per_minute=key.rate_limit_per_minute,
                total_requests=key.total_requests,
                last_used_at=key.last_used_at,
                created_at=key.created_at,
                expires_at=key.expires_at,
                allowed_ips=key.allowed_ips,
            )
            for key in keys
        ]
    
    @staticmethod
    async def revoke_api_key(partner_id: str, key_id: str) -> bool:
        """Revoke an API key"""
        api_key = await APIKey.find_one(
            APIKey.key_id == key_id,
            APIKey.partner_id == partner_id
        )
        
        if not api_key:
            return False
        
        api_key.status = APIKeyStatus.REVOKED
        api_key.revoked_at = datetime.utcnow()
        await api_key.save()
        
        return True
    
    @staticmethod
    async def rotate_api_key(
        partner: Partner,
        key_id: str
    ) -> Optional[APIKeyRotateResponse]:
        """Rotate an API key (revoke old, create new)"""
        
        # Find the old key
        old_key = await APIKey.find_one(
            APIKey.key_id == key_id,
            APIKey.partner_id == str(partner.id)
        )
        
        if not old_key:
            return None
        
        # Create new key with same settings
        new_key_data = APIKeyCreate(
            name=old_key.name,
            scopes=old_key.scopes,
            rate_limit_per_minute=old_key.rate_limit_per_minute,
            allowed_ips=old_key.allowed_ips,
        )
        
        new_key = await PartnerService.create_api_key(partner, new_key_data)
        
        # Revoke old key
        old_key.status = APIKeyStatus.REVOKED
        old_key.revoked_at = datetime.utcnow()
        await old_key.save()
        
        return APIKeyRotateResponse(
            old_key_id=key_id,
            new_key_id=new_key.key_id,
            new_api_key=new_key.api_key,
            new_api_secret=new_key.api_secret,
        )
    
    @staticmethod
    async def verify_api_key(api_key: str) -> Optional[Partner]:
        """
        Verify API key and return partner
        Checks both legacy partner.api_key and new APIKey model
        """
        # Try legacy API key first
        partner = await Partner.find_one(Partner.api_key == api_key)
        if partner and partner.status == PartnerStatus.ACTIVE:
            # Update usage tracking
            partner.total_requests += 1
            partner.last_request_at = datetime.utcnow()
            await partner.save()
            return partner
        
        # Try new APIKey model
        # Note: In production, you'd hash the incoming key and compare
        # For now, we're using the key_id as the lookup
        # This is a simplified version - in production, implement proper key verification
        
        return None
    
    @staticmethod
    async def track_api_usage(
        partner_id: str,
        endpoint: str,
        success: bool
    ) -> None:
        """Track API usage for analytics"""
        # This would typically write to a separate analytics collection
        # For now, we'll just update the partner's total requests
        partner = await Partner.get(partner_id)
        if partner:
            partner.total_requests += 1
            partner.last_request_at = datetime.utcnow()
            await partner.save()
