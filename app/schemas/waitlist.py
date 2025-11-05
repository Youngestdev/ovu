"""
Waitlist subscription schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class WaitlistSubscribeRequest(BaseModel):
    name: Optional[str] = None
    email: EmailStr


class WaitlistSubscribeResponse(BaseModel):
    id: str
    name: Optional[str] = None
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
