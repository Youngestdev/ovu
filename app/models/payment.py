"""
Payment and transaction models
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from beanie import Document
from pydantic import Field
from enum import Enum


class PaymentMethod(str, Enum):
    """Payment methods"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    USSD = "ussd"
    MOBILE_MONEY = "mobile_money"
    WALLET = "wallet"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentProvider(str, Enum):
    """Payment providers"""
    PAYSTACK = "paystack"


class SplitConfig(Document):
    """Split payment configuration for operators"""
    subaccount_code: str
    share_percentage: float
    share_amount: Optional[float] = None
    description: Optional[str] = None


class Payment(Document):
    """Payment model"""
    payment_reference: str = Field(unique=True, index=True)
    booking_id: str = Field(index=True)
    user_id: str = Field(index=True)
    
    # Amount details
    amount: float
    currency: str = "NGN"
    
    # Payment info
    payment_method: PaymentMethod
    payment_provider: PaymentProvider
    provider_reference: Optional[str] = None
    
    # Status
    status: PaymentStatus = PaymentStatus.PENDING
    
    # Split settlement
    split_config: Optional[List[SplitConfig]] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    
    # Additional data
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "payments"
        indexes = [
            "payment_reference",
            "booking_id",
            "user_id",
            "status",
        ]


class TransactionType(str, Enum):
    """Transaction types"""
    BOOKING_PAYMENT = "booking_payment"
    REFUND = "refund"
    PAYOUT = "payout"
    FEE = "fee"


class Transaction(Document):
    """Transaction ledger"""
    transaction_id: str = Field(unique=True, index=True)
    payment_id: Optional[str] = Field(None, index=True)
    booking_id: Optional[str] = Field(None, index=True)
    
    transaction_type: TransactionType
    
    # Parties involved
    from_user_id: Optional[str] = None
    to_user_id: Optional[str] = None
    operator_id: Optional[str] = None
    
    # Amount
    amount: float
    currency: str = "NGN"
    
    # Status
    status: str
    description: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "transactions"
        indexes = [
            "transaction_id",
            "payment_id",
            "booking_id",
            "operator_id",
        ]
