"""
Partner authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class PartnerRegister(BaseModel):
    """Partner registration schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    website: Optional[str] = None
    company_name: str = Field(..., min_length=2, max_length=200)
    business_type: str = Field(..., description="e.g., travel_agency, corporate, reseller")
    tax_id: Optional[str] = None
    business_description: Optional[str] = Field(None, max_length=1000)
    expected_monthly_volume: Optional[int] = Field(None, ge=0)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('business_type')
    def validate_business_type(cls, v):
        """Validate business type"""
        allowed_types = ['travel_agency', 'corporate', 'reseller', 'platform', 'other']
        if v not in allowed_types:
            raise ValueError(f'Business type must be one of: {", ".join(allowed_types)}')
        return v


class PartnerLogin(BaseModel):
    """Partner login schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    partner: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request (authenticated)"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class PartnerApprovalRequest(BaseModel):
    """Admin partner approval/rejection request"""
    action: str = Field(..., pattern="^(approve|reject)$")
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=10000)
    rate_limit_per_day: Optional[int] = Field(None, ge=100, le=1000000)
    notes: Optional[str] = Field(None, max_length=500)
    reason: Optional[str] = Field(None, max_length=500)  # For rejection


class RegistrationResponse(BaseModel):
    """Registration response"""
    message: str
    partner_id: str
    email: str
    status: str


class EmailVerificationResponse(BaseModel):
    """Email verification response"""
    message: str
    status: str
