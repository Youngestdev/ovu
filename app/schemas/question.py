"""
Schemas for Question submissions
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class QuestionRequest(BaseModel):
    email: EmailStr
    question: str
    name: Optional[str] = None


class QuestionResponse(BaseModel):
    id: str
    email: EmailStr
    question: str
    name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
