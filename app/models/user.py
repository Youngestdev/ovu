"""
User model
"""
from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    CUSTOMER = "customer"
    OPERATOR = "operator"
    PARTNER = "partner"
    ADMIN = "admin"


class User(Document):
    """User model"""
    email: EmailStr = Field(unique=True, index=True)
    phone: Optional[str] = Field(None, index=True)
    password_hash: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    operator_id: Optional[str] = None
    partner_id: Optional[str] = None
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "phone",
            "role",
        ]
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
