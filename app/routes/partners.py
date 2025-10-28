"""
Partner API routes with JWT authentication
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.booking import SearchRequest, SearchResult, BookingCreate, BookingResponse
from app.models.partner import Partner
from app.middleware.auth import verify_partner_api_key
from app.services.travu_client import TravuAPIClient
from app.services.nrc_client import NRCAPIClient
from app.models.booking import Booking, TransportType


router = APIRouter(prefix="/api/v1", tags=["Partner API"])


@router.post("/search", response_model=List[SearchResult])
async def partner_search_transport(
    search_req: SearchRequest,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Partner API: Unified search across all transport types"""
    
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
    
    results.sort(key=lambda x: x.price)
    
    return results


@router.post("/bookings", response_model=BookingResponse)
async def partner_create_booking(
    booking_data: BookingCreate,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Partner API: Create a new booking"""
    
    # Similar to the regular booking endpoint but for partners
    # Implementation would be similar to the bookings route
    # For brevity, returning a placeholder
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Partner booking endpoint - implement based on partner requirements"
    )


@router.get("/bookings/{booking_reference}", response_model=BookingResponse)
async def partner_get_booking(
    booking_reference: str,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Partner API: Get booking by reference"""
    
    booking = await Booking.find_one(Booking.booking_reference == booking_reference)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
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
