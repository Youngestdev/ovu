"""
API Key model for partner authentication
"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from enum import Enum


class APIKeyStatus(str, Enum):
    """API key status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class APIKey(Document):
    """API Key model for partner authentication"""
    
    # Key identification
    key_id: str = Field(unique=True, index=True)  # Public key identifier
    key_hash: str  # Hashed API secret (never store plain text)
    name: str  # Friendly name for the key (e.g., "Production Key", "Testing Key")
    
    # Partner relationship
    partner_id: str = Field(index=True)  # Reference to Partner document
    
    # Key metadata
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    
    # Permissions and limits
    scopes: list[str] = ["search", "booking", "payment"]  # API scopes
    rate_limit_per_minute: Optional[int] = None  # Override partner's default
    
    # Usage tracking
    total_requests: int = 0
    last_used_at: Optional[datetime] = None
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Optional expiration
    revoked_at: Optional[datetime] = None
    
    # IP restrictions (optional)
    allowed_ips: list[str] = []  # Empty list means no restriction
    
    class Settings:
        name = "api_keys"
        indexes = [
            "key_id",
            "partner_id",
            "status",
            "created_at",
        ]
