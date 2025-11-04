"""
Waitlist subscription model
"""
from datetime import datetime
from beanie import Document
from pydantic import Field, EmailStr
from pymongo import IndexModel, ASCENDING


class WaitlistSubscription(Document):
    """Represents a user subscribing to the upcoming waitlist/newsletter"""
    name: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "waitlist_subscriptions"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
        ]
