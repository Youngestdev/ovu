"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True
