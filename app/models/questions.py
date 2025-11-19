"""
Questions model for user-submitted questions
"""
from datetime import datetime
from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional


class Question(Document):
    email: EmailStr
    question: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "questions"
