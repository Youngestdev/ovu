"""
Partners interest model
"""
from datetime import datetime
from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from pymongo import IndexModel, ASCENDING


class PartnershipInterest(Document):
    """Represents an entity indicating interest for partnership"""
    company_name: str
    category: str
    email: EmailStr
    phone: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "partnerships"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
        ]
