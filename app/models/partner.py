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
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


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
    
    # API credentials
    api_key: str = Field(unique=True)
    api_secret: str
    
    # Webhook configuration
    webhook_url: Optional[str] = None
    webhook_events: List[WebhookEvent] = []
    webhook_secret: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 10000
    
    # Status
    status: PartnerStatus = PartnerStatus.ACTIVE
    
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
            "status",
        ]
