"""
Payment schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.payment import PaymentMethod


class PaymentInitiate(BaseModel):
    """Payment initiation schema"""
    booking_id: str
    payment_method: PaymentMethod
    callback_url: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema"""
    payment_reference: str
    booking_id: str
    amount: float
    currency: str
    status: str
    payment_url: Optional[str] = None
    authorization_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    """Payment webhook schema from Paystack"""
    event: str
    data: dict


class RefundRequest(BaseModel):
    """Refund request schema"""
    booking_id: str
    reason: str
    amount: Optional[float] = None  # None means full refund
