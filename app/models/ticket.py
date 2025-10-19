"""
Ticket model for e-tickets
"""
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from enum import Enum


class TicketStatus(str, Enum):
    """Ticket status"""
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Ticket(Document):
    """E-ticket model"""
    ticket_number: str = Field(unique=True, index=True)
    booking_id: str = Field(index=True)
    user_id: str = Field(index=True)
    passenger_name: str
    
    # QR Code
    qr_code_data: str
    qr_code_url: Optional[str] = None
    
    # Ticket details
    transport_type: str
    origin: str
    destination: str
    departure_date: datetime
    seat_number: Optional[str] = None
    
    # Status
    status: TicketStatus = TicketStatus.ACTIVE
    
    # Usage tracking
    scanned_at: Optional[datetime] = None
    scanned_by: Optional[str] = None
    
    # PDF
    pdf_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "tickets"
        indexes = [
            "ticket_number",
            "booking_id",
            "user_id",
            "status",
        ]
