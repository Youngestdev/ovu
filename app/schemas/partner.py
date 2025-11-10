from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class PartnershipRequest(BaseModel):
    company_name: str
    email: EmailStr
    phone: str
    category: str


class PartnershipResponses(BaseModel):
    id: str
    name: Optional[str] = None
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
