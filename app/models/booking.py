"""
Booking models for different transport types
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document
from pydantic import Field
from enum import Enum


class TransportType(str, Enum):
    """Transport types"""
    FLIGHT = "flight"
    BUS = "bus"
    TRAIN = "train"


class BookingStatus(str, Enum):
    """Booking status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"


class SeatType(str, Enum):
    """Seat types"""
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST_CLASS = "first_class"
    SLEEPER = "sleeper"
    STANDARD = "standard"


class Passenger(Document):
    """Passenger information"""
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    seat_number: Optional[str] = None
    seat_type: Optional[SeatType] = None


class Booking(Document):
    """Base booking model"""
    booking_reference: str = Field(unique=True, index=True)
    user_id: str = Field(index=True)
    transport_type: TransportType
    status: BookingStatus = BookingStatus.PENDING
    
    # Route information
    origin: str
    destination: str
    departure_date: datetime
    arrival_date: Optional[datetime] = None
    
    # Passengers
    passengers: List[Passenger] = []
    total_passengers: int
    
    # Pricing
    base_price: float
    tax: float
    service_fee: float
    total_price: float
    currency: str = "NGN"
    
    # External references
    provider_booking_id: Optional[str] = None
    operator_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "bookings"
        indexes = [
            "booking_reference",
            "user_id",
            "transport_type",
            "status",
            "departure_date",
        ]


class FlightBooking(Booking):
    """Flight-specific booking"""
    airline: str
    flight_number: str
    aircraft_type: Optional[str] = None
    departure_terminal: Optional[str] = None
    arrival_terminal: Optional[str] = None
    baggage_allowance: Optional[str] = None
    
    class Settings:
        name = "flight_bookings"


class BusBooking(Booking):
    """Bus-specific booking"""
    bus_company: str
    bus_type: str
    departure_terminal: str
    arrival_terminal: str
    bus_number: Optional[str] = None
    amenities: List[str] = []
    
    class Settings:
        name = "bus_bookings"


class TrainBooking(Booking):
    """Train-specific booking"""
    train_service: str
    train_number: str
    coach_number: Optional[str] = None
    departure_station: str
    arrival_station: str
    train_class: str
    
    class Settings:
        name = "train_bookings"
