"""
Partner API schemas for B2B integration
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from pydantic_mongo import PydanticObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.partner import PartnerStatus, WebhookEvent
from app.models.api_key import APIKeyStatus


# Partnership Request (legacy - keeping for backward compatibility)
class PartnershipRequest(BaseModel):
    company_name: str
    email: EmailStr
    phone: str
    category: str


class PartnershipResponses(BaseModel):
    id: PydanticObjectId
    name: Optional[str] = None
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# New B2B Partner Schemas

class PartnerCreate(BaseModel):
    """Schema for creating a new business partner"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str
    website: Optional[HttpUrl] = None
    
    # Business information
    company_name: str = Field(..., min_length=2, max_length=200)
    business_type: str  # e.g., "travel_agency", "corporate", "reseller"
    tax_id: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000)
    rate_limit_per_day: int = Field(default=10000, ge=1, le=1000000)


class PartnerUpdate(BaseModel):
    """Schema for updating partner information"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    rate_limit_per_day: Optional[int] = Field(None, ge=1, le=1000000)


class PartnerResponse(BaseModel):
    """Schema for partner data response"""
    id: str
    partner_code: str
    name: str
    email: EmailStr
    phone: str
    website: Optional[str] = None
    company_name: Optional[str] = None
    business_type: Optional[str] = None
    status: PartnerStatus
    rate_limit_per_minute: int
    rate_limit_per_day: int
    total_requests: int
    last_request_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# API Key Management Schemas

class APIKeyCreate(BaseModel):
    """Schema for creating a new API key"""
    name: str = Field(..., min_length=2, max_length=100, description="Friendly name for the key")
    scopes: List[str] = Field(default=["search", "booking", "payment"], description="API scopes")
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000, description="Override partner's rate limit")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Key expiration in days")
    allowed_ips: List[str] = Field(default=[], description="IP whitelist (empty = no restriction)")


class APIKeyResponse(BaseModel):
    """Schema for API key response (with masked secret)"""
    key_id: str
    name: str
    key_preview: str  # First 8 chars of the key for identification
    partner_id: str
    status: APIKeyStatus
    scopes: List[str]
    rate_limit_per_minute: Optional[int] = None
    total_requests: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    allowed_ips: List[str]


class APIKeyCreateResponse(BaseModel):
    """Schema for API key creation response (includes full key once)"""
    key_id: str
    name: str
    api_key: str  # Full key - only shown once!
    api_secret: str  # Full secret - only shown once!
    status: APIKeyStatus
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "key_id": "key_abc123",
                "name": "Production Key",
                "api_key": "ovu_live_abc123def456ghi789",
                "api_secret": "sk_live_xyz789uvw456rst123",
                "status": "active",
                "scopes": ["search", "booking", "payment"],
                "created_at": "2024-12-20T12:00:00Z",
                "expires_at": None
            }
        }


class APIKeyRotateResponse(BaseModel):
    """Schema for API key rotation response"""
    old_key_id: str
    new_key_id: str
    new_api_key: str
    new_api_secret: str
    message: str = "API key rotated successfully. Old key has been revoked."


# Usage Analytics Schemas

class UsageStatsDaily(BaseModel):
    """Daily usage statistics"""
    date: str
    total_requests: int
    search_requests: int
    booking_requests: int
    payment_requests: int
    successful_requests: int
    failed_requests: int


class PartnerUsageStats(BaseModel):
    """Partner usage statistics"""
    partner_id: str
    partner_name: str
    period_start: datetime
    period_end: datetime
    
    # Overall stats
    total_requests: int
    total_bookings: int
    total_revenue: float
    
    # Daily breakdown
    daily_stats: List[UsageStatsDaily]
    
    # Rate limit info
    current_rate_limit_per_minute: int
    current_rate_limit_per_day: int
    requests_today: int
    
    # API key stats
    active_api_keys: int
    total_api_keys: int


# Webhook Configuration Schemas

class WebhookConfigUpdate(BaseModel):
    """Schema for updating webhook configuration"""
    webhook_url: Optional[HttpUrl] = Field(None, description="Webhook endpoint URL")
    webhook_events: List[WebhookEvent] = Field(default=[], description="Events to subscribe to")
    webhook_secret: Optional[str] = Field(None, min_length=32, description="Secret for signature verification")


class WebhookConfigResponse(BaseModel):
    """Schema for webhook configuration response"""
    webhook_url: Optional[str] = None
    webhook_events: List[WebhookEvent]
    webhook_secret_preview: Optional[str] = None  # First 8 chars
    is_configured: bool


class WebhookTestRequest(BaseModel):
    """Schema for webhook test request"""
    event_type: WebhookEvent = Field(default=WebhookEvent.BOOKING_CREATED)


class WebhookTestResponse(BaseModel):
    """Schema for webhook test response"""
    success: bool
    message: str
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
