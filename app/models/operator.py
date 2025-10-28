"""
Operator model for transport operators
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from beanie import Document
from pydantic import Field, EmailStr
from enum import Enum


class OperatorType(str, Enum):
    """Operator types"""
    AIRLINE = "airline"
    BUS_COMPANY = "bus_company"
    TRAIN_SERVICE = "train_service"


class OperatorStatus(str, Enum):
    """Operator status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Operator(Document):
    """Transport operator model"""
    operator_code: str = Field(unique=True, index=True)
    name: str
    operator_type: OperatorType
    
    # Contact information
    email: EmailStr
    phone: str
    website: Optional[str] = None
    
    # Business details
    business_name: str
    business_registration_number: str
    tax_id: Optional[str] = None
    
    # Payment details for split settlements
    paystack_subaccount_code: Optional[str] = None
    commission_percentage: float = 10.0  # Default 10% commission
    
    # Status
    status: OperatorStatus = OperatorStatus.ACTIVE
    
    # Verification
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "operators"
        indexes = [
            "operator_code",
            "operator_type",
            "status",
        ]
