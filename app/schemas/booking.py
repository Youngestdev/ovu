"""
Booking schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.booking import TransportType, SeatType


class PassengerCreate(BaseModel):
    """Passenger creation schema"""
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    seat_type: Optional[SeatType] = None


class SearchRequest(BaseModel):
    """Unified search request"""
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    passengers: int = Field(ge=1, le=10)
    transport_types: List[TransportType] = Field(
        default=[TransportType.FLIGHT, TransportType.BUS, TransportType.TRAIN]
    )
    seat_type: Optional[SeatType] = None


class SearchResult(BaseModel):
    """Search result item"""
    transport_type: TransportType
    provider: str
    origin: str
    destination: str
    departure_date: datetime
    arrival_date: Optional[datetime] = None
    price: float
    currency: str = "NGN"
    available_seats: int
    duration_minutes: Optional[int] = None
    operator_id: Optional[str] = None
    provider_reference: str
    
    # Type-specific details
    flight_number: Optional[str] = None
    airline: Optional[str] = None
    bus_type: Optional[str] = None
    bus_company: Optional[str] = None
    train_number: Optional[str] = None
    train_service: Optional[str] = None


class BookingCreate(BaseModel):
    """Booking creation schema"""
    provider_reference: str
    transport_type: TransportType
    passengers: List[PassengerCreate]
    
    # Optional fields
    metadata: Optional[dict] = {}


class BookingResponse(BaseModel):
    """Booking response schema"""
    id: str
    booking_reference: str
    user_id: str
    transport_type: TransportType
    status: str
    origin: str
    destination: str
    departure_date: datetime
    total_passengers: int
    total_price: float
    currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True
