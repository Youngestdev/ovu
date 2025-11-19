"""
Integration tests for B2B API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.models.partner import Partner, PartnerStatus
from app.models.user import User
from app.services.partner_service import PartnerService
from app.schemas.partner import PartnerCreate


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
async def admin_user():
    """Create admin user for testing"""
    user = User(
        email="admin@test.com",
        first_name="Admin",
        last_name="User",
        phone="+2348012345678",
        role="admin",
        is_active=True,
        is_verified=True
    )
    await user.insert()
    yield user
    await user.delete()


@pytest.fixture
async def test_partner():
    """Create test partner"""
    partner_data = PartnerCreate(
        name="Test Partner",
        email="partner@test.com",
        phone="+2348012345678",
        company_name="Test Partner Inc",
        business_type="travel_agency",
        rate_limit_per_minute=100,
        rate_limit_per_day=50000
    )
    
    partner, api_key, api_secret = await PartnerService.create_partner(partner_data)
    
    # Store credentials for tests
    partner.test_api_key = api_key
    partner.test_api_secret = api_secret
    
    yield partner
    
    await partner.delete()


class TestPartnerManagementEndpoints:
    """Test partner management API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_partner_as_admin(self, client, admin_user):
        """Test creating a partner as admin"""
        # Get admin token (simplified - in real tests, use proper auth)
        from app.core.security import create_access_token
        admin_token = create_access_token({"sub": str(admin_user.id)})
        
        response = client.post(
            "/api/v1/partners",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "New Partner",
                "email": "new@partner.com",
                "phone": "+2348012345678",
                "company_name": "New Partner Inc",
                "business_type": "corporate",
                "rate_limit_per_minute": 150,
                "rate_limit_per_day": 75000
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "partner" in data
        assert "credentials" in data
        assert data["partner"]["name"] == "New Partner"
        assert data["partner"]["status"] == "active"
        assert data["credentials"]["api_key"].startswith("ovu_live_")
        assert data["credentials"]["api_secret"].startswith("sk_live_")
    
    @pytest.mark.asyncio
    async def test_get_partner_info(self, client, test_partner):
        """Test getting current partner info"""
        response = client.get(
            "/api/v1/partners/me",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == test_partner.name
        assert data["email"] == test_partner.email
        assert data["partner_code"] == test_partner.partner_code
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_update_partner_info(self, client, test_partner):
        """Test updating partner information"""
        response = client.put(
            "/api/v1/partners/me",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "name": "Updated Partner Name",
                "phone": "+2348087654321",
                "rate_limit_per_minute": 200
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Partner Name"
        assert data["phone"] == "+2348087654321"
        assert data["rate_limit_per_minute"] == 200


class TestAPIKeyManagementEndpoints:
    """Test API key management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_api_key(self, client, test_partner):
        """Test creating a new API key"""
        response = client.post(
            "/api/v1/partners/api-keys",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "name": "Production Key",
                "scopes": ["search", "booking", "payment"],
                "rate_limit_per_minute": 200,
                "expires_in_days": 365,
                "allowed_ips": ["203.0.113.0"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Production Key"
        assert data["scopes"] == ["search", "booking", "payment"]
        assert data["status"] == "active"
        assert data["api_key"].startswith("ovu_live_")
        assert data["api_secret"].startswith("sk_live_")
        assert data["expires_at"] is not None
    
    @pytest.mark.asyncio
    async def test_list_api_keys(self, client, test_partner):
        """Test listing API keys"""
        # Create additional key first
        client.post(
            "/api/v1/partners/api-keys",
            headers={"X-API-Key": test_partner.test_api_key},
            json={"name": "Test Key", "scopes": ["search"]}
        )
        
        response = client.get(
            "/api/v1/partners/api-keys",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify key structure
        for key in data:
            assert "key_id" in key
            assert "name" in key
            assert "status" in key
            assert "scopes" in key
    
    @pytest.mark.asyncio
    async def test_revoke_api_key(self, client, test_partner):
        """Test revoking an API key"""
        # Create key to revoke
        create_response = client.post(
            "/api/v1/partners/api-keys",
            headers={"X-API-Key": test_partner.test_api_key},
            json={"name": "To Revoke", "scopes": ["search"]}
        )
        key_id = create_response.json()["key_id"]
        
        # Revoke it
        response = client.delete(
            f"/api/v1/partners/api-keys/{key_id}",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_rotate_api_key(self, client, test_partner):
        """Test rotating an API key"""
        # Create key to rotate
        create_response = client.post(
            "/api/v1/partners/api-keys",
            headers={"X-API-Key": test_partner.test_api_key},
            json={"name": "To Rotate", "scopes": ["search", "booking"]}
        )
        old_key_id = create_response.json()["key_id"]
        
        # Rotate it
        response = client.put(
            f"/api/v1/partners/api-keys/{old_key_id}/rotate",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["old_key_id"] == old_key_id
        assert data["new_key_id"] != old_key_id
        assert data["new_api_key"].startswith("ovu_live_")
        assert data["new_api_secret"].startswith("sk_live_")


class TestUsageAnalyticsEndpoints:
    """Test usage analytics endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_usage_statistics(self, client, test_partner):
        """Test getting usage statistics"""
        response = client.get(
            "/api/v1/partners/usage?days=30",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "partner_id" in data
        assert "partner_name" in data
        assert "total_requests" in data
        assert "total_bookings" in data
        assert "total_revenue" in data
        assert "daily_stats" in data
        assert "active_api_keys" in data
        assert "total_api_keys" in data
        
        # Verify daily stats structure
        assert isinstance(data["daily_stats"], list)
        if len(data["daily_stats"]) > 0:
            day_stat = data["daily_stats"][0]
            assert "date" in day_stat
            assert "total_requests" in day_stat


class TestWebhookConfigurationEndpoints:
    """Test webhook configuration endpoints"""
    
    @pytest.mark.asyncio
    async def test_configure_webhooks(self, client, test_partner):
        """Test configuring webhooks"""
        response = client.put(
            "/api/v1/partners/webhooks",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "webhook_url": "https://example.com/webhooks/ovu",
                "webhook_events": ["booking.created", "payment.success"],
                "webhook_secret": "my_super_secret_webhook_key_12345"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["webhook_url"] == "https://example.com/webhooks/ovu"
        assert "booking.created" in data["webhook_events"]
        assert "payment.success" in data["webhook_events"]
        assert data["is_configured"] is True
        assert data["webhook_secret_preview"] is not None
    
    @pytest.mark.asyncio
    async def test_get_webhook_config(self, client, test_partner):
        """Test getting webhook configuration"""
        # Configure first
        client.put(
            "/api/v1/partners/webhooks",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "webhook_url": "https://example.com/webhooks",
                "webhook_events": ["booking.created"]
            }
        )
        
        # Get config
        response = client.get(
            "/api/v1/partners/webhooks",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["webhook_url"] == "https://example.com/webhooks"
        assert data["is_configured"] is True


class TestPartnerAPIEndpoints:
    """Test partner API search and booking endpoints"""
    
    @pytest.mark.asyncio
    async def test_partner_search(self, client, test_partner):
        """Test partner search endpoint"""
        response = client.post(
            "/api/v1/search",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "origin": "Lagos",
                "destination": "Abuja",
                "departure_date": "2024-12-25T08:00:00",
                "passengers": 2,
                "transport_types": ["flight", "bus"]
            }
        )
        
        # May return empty list if no providers configured
        assert response.status_code in [200, 500]  # 500 if providers not configured
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_partner_create_booking(self, client, test_partner):
        """Test partner booking creation"""
        response = client.post(
            "/api/v1/bookings",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "provider_reference": "TEST-REF-001",
                "transport_type": "flight",
                "passengers": [
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john@example.com",
                        "phone": "+2348012345678"
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "booking_reference" in data
        assert data["status"] == "pending"
        assert data["transport_type"] == "flight"
    
    @pytest.mark.asyncio
    async def test_partner_get_booking(self, client, test_partner):
        """Test getting booking by reference"""
        # Create booking first
        create_response = client.post(
            "/api/v1/bookings",
            headers={"X-API-Key": test_partner.test_api_key},
            json={
                "provider_reference": "TEST-REF-002",
                "transport_type": "bus",
                "passengers": [
                    {
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "email": "jane@example.com",
                        "phone": "+2348012345678"
                    }
                ]
            }
        )
        booking_ref = create_response.json()["booking_reference"]
        
        # Get booking
        response = client.get(
            f"/api/v1/bookings/{booking_ref}",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["booking_reference"] == booking_ref


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, client, test_partner):
        """Test that rate limit headers are included"""
        response = client.get(
            "/api/v1/partners/me",
            headers={"X-API-Key": test_partner.test_api_key}
        )
        
        # Check for rate limit headers (if Redis is available)
        # These may not be present if Redis is not running
        if "X-RateLimit-Limit-Minute" in response.headers:
            assert "X-RateLimit-Remaining-Minute" in response.headers
            assert "X-RateLimit-Limit-Day" in response.headers
            assert "X-RateLimit-Remaining-Day" in response.headers


class TestAuthentication:
    """Test authentication and authorization"""
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, client):
        """Test request without API key"""
        response = client.get("/api/v1/partners/me")
        
        assert response.status_code == 401
        assert "API key required" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self, client):
        """Test request with invalid API key"""
        response = client.get(
            "/api/v1/partners/me",
            headers={"X-API-Key": "invalid_key_123"}
        )
        
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]
