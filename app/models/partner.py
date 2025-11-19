"""
Partner model for API integrations
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from beanie import Document
from pydantic import Field, EmailStr
from enum import Enum


class PartnerStatus(str, Enum):
    """Partner status"""
    PENDING_VERIFICATION = "pending_verification"  # Email not verified
    PENDING_APPROVAL = "pending_approval"          # Email verified, awaiting admin approval
    ACTIVE = "active"                              # Approved and active
    SUSPENDED = "suspended"                        # Temporarily suspended
    REJECTED = "rejected"                          # Application rejected
    INACTIVE = "inactive"                          # Deactivated


class WebhookEvent(str, Enum):
    """Webhook event types"""
    BOOKING_CREATED = "booking.created"
    BOOKING_CONFIRMED = "booking.confirmed"
    BOOKING_CANCELLED = "booking.cancelled"
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    TICKET_GENERATED = "ticket.generated"


class Partner(Document):
    """Partner/API consumer model"""
    partner_code: str = Field(unique=True, index=True)
    name: str
    
    # Contact information
    email: EmailStr
    phone: str
    website: Optional[str] = None
    
    # Business information
    company_name: Optional[str] = None
    business_type: Optional[str] = None  # e.g., "travel_agency", "corporate", "reseller"
    tax_id: Optional[str] = None
    
    # API credentials (legacy - for backward compatibility)
    # New partners should use APIKey model instead
    api_key: str = Field(unique=True)
    api_secret: str
    
    # Webhook configuration
    webhook_url: Optional[str] = None
    webhook_events: List[WebhookEvent] = []
    webhook_secret: Optional[str] = None
    
    # Authentication (for dashboard access)
    password_hash: Optional[str] = None
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    
    # Onboarding information
    business_description: Optional[str] = None
    expected_monthly_volume: Optional[int] = None
    
    # Approval tracking
    approval_notes: Optional[str] = None
    approved_by: Optional[str] = None  # Admin user ID
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    
    # Password reset
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 10000
    
    # Status
    status: PartnerStatus = PartnerStatus.PENDING_VERIFICATION
    
    # Usage tracking
    total_requests: int = 0
    last_request_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "partners"
        indexes = [
            "partner_code",
            "api_key",
            "email",
            "status",
        ]
