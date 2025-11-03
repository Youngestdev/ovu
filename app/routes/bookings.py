"""
Booking routes for unified search and booking management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from app.schemas.booking import SearchRequest, SearchResult, BookingCreate, BookingResponse
from app.models.booking import Booking, FlightBooking, BusBooking, TrainBooking, BookingStatus, TransportType
from app.models.user import User
from app.middleware.auth import get_current_user
from app.services.travu_client import TravuAPIClient
from app.services.nrc_client import NRCAPIClient
from app.services.ticket_service import TicketService
from app.services.notification_service import NotificationService
from app.utils.helpers import generate_reference


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/search", response_model=List[SearchResult])
async def search_transport(search_req: SearchRequest):
    """Unified search across all transport types"""
    
    results = []
    
    # Search flights
    if TransportType.FLIGHT in search_req.transport_types:
        travu_client = TravuAPIClient()
        flight_results = await travu_client.search_flights(search_req)
        results.extend(flight_results)
    
    # Search buses
    if TransportType.BUS in search_req.transport_types:
        travu_client = TravuAPIClient()
        bus_results = await travu_client.search_buses(search_req)
        results.extend(bus_results)
    
    # Search trains
    if TransportType.TRAIN in search_req.transport_types:
        nrc_client = NRCAPIClient()
        train_results = await nrc_client.search_trains(search_req)
        results.extend(train_results)
    
    # Sort by price
    results.sort(key=lambda x: x.price)
    
    return results


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new booking"""
    
    # Generate booking reference
    booking_reference = generate_reference("BKG")
    
    # Get search result details (in production, this would come from cache or re-query)
    # For now, we'll create a mock booking
    
    base_booking_data = {
        "booking_reference": booking_reference,
        "user_id": str(current_user.id),
        "transport_type": booking_data.transport_type,
        "status": BookingStatus.PENDING,
        "passengers": booking_data.passengers,
        "total_passengers": len(booking_data.passengers),
        "provider_booking_id": booking_data.provider_reference,
        "metadata": booking_data.metadata,
    }
    
    # Create transport-specific booking
    if booking_data.transport_type == TransportType.FLIGHT:
        # Mock flight data
        booking = FlightBooking(
            **base_booking_data,
            origin="Lagos",
            destination="Abuja",
            departure_date=datetime.utcnow(),
            airline="Air Peace",
            flight_number="AA101",
            base_price=40000.0,
            tax=5000.0,
            service_fee=2000.0,
            total_price=47000.0,
        )
    elif booking_data.transport_type == TransportType.BUS:
        booking = BusBooking(
            **base_booking_data,
            origin="Lagos",
            destination="Ibadan",
            departure_date=datetime.utcnow(),
            bus_company="GUO Transport",
            bus_type="Luxury",
            departure_terminal="Ojota Terminal",
            arrival_terminal="Ibadan Main",
            base_price=7000.0,
            tax=500.0,
            service_fee=500.0,
            total_price=8000.0,
        )
    elif booking_data.transport_type == TransportType.TRAIN:
        booking = TrainBooking(
            **base_booking_data,
            origin="Lagos",
            destination="Ibadan",
            departure_date=datetime.utcnow(),
            train_service="Lagos-Ibadan Express",
            train_number="NRC-001",
            departure_station="Ebute Metta",
            arrival_station="Ibadan Station",
            train_class="Standard",
            base_price=3000.0,
            tax=300.0,
            service_fee=200.0,
            total_price=3500.0,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transport type"
        )
    
    await booking.save()
    
    # Send booking confirmation
    notification_service = NotificationService()
    await notification_service.send_booking_confirmation(
        email=current_user.email,
        phone=current_user.phone,
        booking_reference=booking_reference,
        booking_details={
            "customer_name": f"{current_user.first_name} {current_user.last_name}",
            "transport_type": booking.transport_type,
            "origin": booking.origin,
            "destination": booking.destination,
            "departure_date": booking.departure_date.strftime("%Y-%m-%d %H:%M"),
            "total_passengers": booking.total_passengers,
            "total_price": booking.total_price,
        }
    )
    
    return BookingResponse(
        id=str(booking.id),
        booking_reference=booking.booking_reference,
        user_id=booking.user_id,
        transport_type=booking.transport_type,
        status=booking.status,
        origin=booking.origin,
        destination=booking.destination,
        departure_date=booking.departure_date,
        total_passengers=booking.total_passengers,
        total_price=booking.total_price,
        currency=booking.currency,
        created_at=booking.created_at,
    )


@router.get("/", response_model=List[BookingResponse])
async def get_user_bookings(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    """Get user's bookings"""
    
    bookings = await Booking.find(
        Booking.user_id == str(current_user.id)
    ).skip(skip).limit(limit).to_list()
    
    return [
        BookingResponse(
            id=str(booking.id),
            booking_reference=booking.booking_reference,
            user_id=booking.user_id,
            transport_type=booking.transport_type,
            status=booking.status,
            origin=booking.origin,
            destination=booking.destination,
            departure_date=booking.departure_date,
            total_passengers=booking.total_passengers,
            total_price=booking.total_price,
            currency=booking.currency,
            created_at=booking.created_at,
        )
        for booking in bookings
    ]


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific booking"""
    
    booking = await Booking.get(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user owns the booking
    if booking.user_id != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    return BookingResponse(
        id=str(booking.id),
        booking_reference=booking.booking_reference,
        user_id=booking.user_id,
        transport_type=booking.transport_type,
        status=booking.status,
        origin=booking.origin,
        destination=booking.destination,
        departure_date=booking.departure_date,
        total_passengers=booking.total_passengers,
        total_price=booking.total_price,
        currency=booking.currency,
        created_at=booking.created_at,
    )


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking"""
    
    booking = await Booking.get(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user owns the booking
    if booking.user_id != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )
    
    # Check if booking can be cancelled
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking cannot be cancelled"
        )
    
    # Update booking status
    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    await booking.save()
    
    return {"message": "Booking cancelled successfully"}
