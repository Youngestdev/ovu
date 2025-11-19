"""
Partner API routes with comprehensive B2B management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime, timedelta

# Schemas
from app.schemas.booking import SearchRequest, SearchResult, BookingCreate, BookingResponse
from app.schemas.partner import (
    PartnerCreate, PartnerUpdate, PartnerResponse,
    APIKeyCreate, APIKeyCreateResponse, APIKeyResponse, APIKeyRotateResponse,
    PartnerUsageStats, UsageStatsDaily,
    WebhookConfigUpdate, WebhookConfigResponse, WebhookTestRequest, WebhookTestResponse
)

# Models
from app.models.partner import Partner
from app.models.booking import Booking, TransportType, BookingStatus
from app.models.user import User

# Services
from app.services.partner_service import PartnerService
from app.services.webhook_service import WebhookService
from app.services.travu_client import TravuAPIClient
from app.services.nrc_client import NRCAPIClient

# Middleware
from app.middleware.auth import verify_partner_api_key, get_current_admin


router = APIRouter(prefix="/api/v1", tags=["Partner API"])


# ============================================================================
# PARTNER MANAGEMENT ENDPOINTS (Admin Only)
# ============================================================================

@router.post("/partners", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_partner(
    partner_data: PartnerCreate,
    admin: User = Depends(get_current_admin)
):
    """
    Create a new business partner (Admin only)
    Returns partner info with initial API credentials
    """
    # Check if partner with email already exists
    existing = await Partner.find_one(Partner.email == partner_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner with this email already exists"
        )
    
    # Create partner
    partner, api_key, api_secret = await PartnerService.create_partner(partner_data)
    
    return {
        "partner": PartnerResponse(
            id=str(partner.id),
            partner_code=partner.partner_code,
            name=partner.name,
            email=partner.email,
            phone=partner.phone,
            website=partner.website,
            company_name=partner.company_name,
            business_type=partner.business_type,
            status=partner.status,
            rate_limit_per_minute=partner.rate_limit_per_minute,
            rate_limit_per_day=partner.rate_limit_per_day,
            total_requests=partner.total_requests,
            last_request_at=partner.last_request_at,
            created_at=partner.created_at,
            updated_at=partner.updated_at,
        ),
        "credentials": {
            "api_key": api_key,
            "api_secret": api_secret,
            "note": "Store these credentials securely. The secret will not be shown again."
        }
    }


# ============================================================================
# PARTNER SELF-SERVICE ENDPOINTS
# ============================================================================

@router.get("/partners/me", response_model=PartnerResponse)
async def get_current_partner(partner: Partner = Depends(verify_partner_api_key)):
    """Get current partner information"""
    return PartnerResponse(
        id=str(partner.id),
        partner_code=partner.partner_code,
        name=partner.name,
        email=partner.email,
        phone=partner.phone,
        website=partner.website,
        company_name=partner.company_name,
        business_type=partner.business_type,
        status=partner.status,
        rate_limit_per_minute=partner.rate_limit_per_minute,
        rate_limit_per_day=partner.rate_limit_per_day,
        total_requests=partner.total_requests,
        last_request_at=partner.last_request_at,
        created_at=partner.created_at,
        updated_at=partner.updated_at,
    )


@router.put("/partners/me", response_model=PartnerResponse)
async def update_current_partner(
    update_data: PartnerUpdate,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Update current partner information"""
    
    # Update fields
    if update_data.name is not None:
        partner.name = update_data.name
    if update_data.phone is not None:
        partner.phone = update_data.phone
    if update_data.website is not None:
        partner.website = str(update_data.website)
    if update_data.rate_limit_per_minute is not None:
        partner.rate_limit_per_minute = update_data.rate_limit_per_minute
    if update_data.rate_limit_per_day is not None:
        partner.rate_limit_per_day = update_data.rate_limit_per_day
    
    partner.updated_at = datetime.utcnow()
    await partner.save()
    
    return PartnerResponse(
        id=str(partner.id),
        partner_code=partner.partner_code,
        name=partner.name,
        email=partner.email,
        phone=partner.phone,
        website=partner.website,
        company_name=partner.company_name,
        business_type=partner.business_type,
        status=partner.status,
        rate_limit_per_minute=partner.rate_limit_per_minute,
        rate_limit_per_day=partner.rate_limit_per_day,
        total_requests=partner.total_requests,
        last_request_at=partner.last_request_at,
        created_at=partner.created_at,
        updated_at=partner.updated_at,
    )


# ============================================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/partners/api-keys", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Generate a new API key for the partner"""
    return await PartnerService.create_api_key(partner, key_data)


@router.get("/partners/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(partner: Partner = Depends(verify_partner_api_key)):
    """List all API keys for the partner"""
    return await PartnerService.list_api_keys(str(partner.id))


@router.delete("/partners/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Revoke an API key"""
    success = await PartnerService.revoke_api_key(str(partner.id), key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return None


@router.put("/partners/api-keys/{key_id}/rotate", response_model=APIKeyRotateResponse)
async def rotate_api_key(
    key_id: str,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Rotate an API key (revoke old, create new with same settings)"""
    result = await PartnerService.rotate_api_key(partner, key_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return result


# ============================================================================
# USAGE ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/partners/usage", response_model=PartnerUsageStats)
async def get_usage_statistics(
    days: int = 30,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Get usage statistics for the partner"""
    
    # Calculate period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get bookings for revenue calculation
    bookings = await Booking.find(
        Booking.created_at >= start_date,
        Booking.created_at <= end_date
    ).to_list()
    
    total_bookings = len(bookings)
    total_revenue = sum(b.total_price for b in bookings if b.status == BookingStatus.PAID)
    
    # Get API keys count
    api_keys = await PartnerService.list_api_keys(str(partner.id))
    active_keys = sum(1 for k in api_keys if k.status == "active")
    
    # Generate daily stats (simplified - in production, use aggregation)
    daily_stats = []
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_stats.append(UsageStatsDaily(
            date=date,
            total_requests=0,  # Would come from analytics DB
            search_requests=0,
            booking_requests=0,
            payment_requests=0,
            successful_requests=0,
            failed_requests=0,
        ))
    
    return PartnerUsageStats(
        partner_id=str(partner.id),
        partner_name=partner.name,
        period_start=start_date,
        period_end=end_date,
        total_requests=partner.total_requests,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        daily_stats=daily_stats,
        current_rate_limit_per_minute=partner.rate_limit_per_minute,
        current_rate_limit_per_day=partner.rate_limit_per_day,
        requests_today=0,  # Would come from analytics DB
        active_api_keys=active_keys,
        total_api_keys=len(api_keys),
    )


# ============================================================================
# WEBHOOK CONFIGURATION ENDPOINTS
# ============================================================================

@router.put("/partners/webhooks", response_model=WebhookConfigResponse)
async def configure_webhooks(
    config: WebhookConfigUpdate,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Configure webhook settings for the partner"""
    
    if config.webhook_url is not None:
        partner.webhook_url = str(config.webhook_url)
    
    if config.webhook_events is not None:
        partner.webhook_events = config.webhook_events
    
    if config.webhook_secret is not None:
        partner.webhook_secret = config.webhook_secret
    
    partner.updated_at = datetime.utcnow()
    await partner.save()
    
    return WebhookConfigResponse(
        webhook_url=partner.webhook_url,
        webhook_events=partner.webhook_events,
        webhook_secret_preview=partner.webhook_secret[:8] + "..." if partner.webhook_secret else None,
        is_configured=bool(partner.webhook_url and partner.webhook_events),
    )


@router.get("/partners/webhooks", response_model=WebhookConfigResponse)
async def get_webhook_config(partner: Partner = Depends(verify_partner_api_key)):
    """Get current webhook configuration"""
    return WebhookConfigResponse(
        webhook_url=partner.webhook_url,
        webhook_events=partner.webhook_events,
        webhook_secret_preview=partner.webhook_secret[:8] + "..." if partner.webhook_secret else None,
        is_configured=bool(partner.webhook_url and partner.webhook_events),
    )


@router.post("/partners/webhooks/test", response_model=WebhookTestResponse)
async def test_webhook(
    test_request: WebhookTestRequest,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Test webhook configuration by sending a test event"""
    
    success, status_code, response_time, error = await WebhookService.test_webhook(
        partner=partner,
        event_type=test_request.event_type
    )
    
    return WebhookTestResponse(
        success=success,
        message="Webhook test successful" if success else f"Webhook test failed: {error}",
        status_code=status_code,
        response_time_ms=response_time,
    )


# ============================================================================
# PARTNER API - TRANSPORT SEARCH & BOOKING
# ============================================================================

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
    
    # Track usage
    await PartnerService.track_api_usage(str(partner.id), "search", True)
    
    return results


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def partner_create_booking(
    booking_data: BookingCreate,
    partner: Partner = Depends(verify_partner_api_key)
):
    """Partner API: Create a new booking"""
    
    # Create booking (simplified - in production, integrate with actual booking service)
    from app.utils.helpers import generate_booking_reference
    
    booking = Booking(
        booking_reference=generate_booking_reference(),
        user_id=str(partner.id),  # Using partner ID as user
        transport_type=booking_data.transport_type,
        status=BookingStatus.PENDING,
        origin=booking_data.origin if hasattr(booking_data, 'origin') else "Unknown",
        destination=booking_data.destination if hasattr(booking_data, 'destination') else "Unknown",
        departure_date=datetime.utcnow(),
        total_passengers=len(booking_data.passengers),
        total_price=0.0,  # Would be calculated from provider
        currency="NGN",
        provider_reference=booking_data.provider_reference,
    )
    
    await booking.insert()
    
    # Send webhook notification
    await WebhookService.notify_booking_created(partner, {
        "booking_reference": booking.booking_reference,
        "status": booking.status,
        "transport_type": booking.transport_type,
    })
    
    # Track usage
    await PartnerService.track_api_usage(str(partner.id), "booking", True)
    
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