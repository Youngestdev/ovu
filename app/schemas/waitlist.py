"""
Waitlist subscription schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime


class WaitlistSubscribeRequest(BaseModel):
    name: str
    email: EmailStr


class WaitlistSubscribeResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
