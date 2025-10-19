"""
Operator dashboard routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.user import User
from app.models.operator import Operator
from app.models.booking import Booking
from app.models.payment import Payment, Transaction
from app.middleware.auth import get_current_operator
from pymongo import DESCENDING


router = APIRouter(prefix="/operators", tags=["Operators"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_operator)
):
    """Get operator dashboard data"""
    
    # Get operator
    operator = await Operator.find_one(Operator.operator_code == current_user.operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operator not found"
        )
    
    # Get date ranges
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get bookings count
    total_bookings = await Booking.find(
        Booking.operator_id == str(operator.id)
    ).count()
    
    today_bookings = await Booking.find(
        Booking.operator_id == str(operator.id),
        Booking.created_at >= today
    ).count()
    
    # Get revenue
    total_revenue = 0.0
    today_revenue = 0.0
    
    payments = await Payment.find(
        Payment.status == "success"
    ).to_list()
    
    for payment in payments:
        booking = await Booking.get(payment.booking_id)
        if booking and booking.operator_id == str(operator.id):
            total_revenue += payment.amount
            if payment.paid_at and payment.paid_at >= today:
                today_revenue += payment.amount
    
    return {
        "operator": {
            "name": operator.name,
            "operator_code": operator.operator_code,
            "type": operator.operator_type,
            "status": operator.status,
        },
        "stats": {
            "total_bookings": total_bookings,
            "today_bookings": today_bookings,
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
        }
    }


@router.get("/bookings")
async def get_operator_bookings(
    current_user: User = Depends(get_current_operator),
    skip: int = 0,
    limit: int = 20,
):
    """Get operator's bookings"""
    
    operator = await Operator.find_one(Operator.operator_code == current_user.operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operator not found"
        )
    
    bookings = await Booking.find(
        Booking.operator_id == str(operator.id)
    ).skip(skip).limit(limit).sort([("created_at", DESCENDING)]).to_list()
    
    return {
        "bookings": [
            {
                "id": str(booking.id),
                "booking_reference": booking.booking_reference,
                "transport_type": booking.transport_type,
                "status": booking.status,
                "origin": booking.origin,
                "destination": booking.destination,
                "departure_date": booking.departure_date,
                "total_passengers": booking.total_passengers,
                "total_price": booking.total_price,
                "created_at": booking.created_at,
            }
            for booking in bookings
        ],
        "total": await Booking.find(Booking.operator_id == str(operator.id)).count()
    }


@router.get("/sales")
async def get_sales_analytics(
    current_user: User = Depends(get_current_operator),
    days: int = 30,
):
    """Get sales analytics"""
    
    operator = await Operator.find_one(Operator.operator_code == current_user.operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operator not found"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get bookings in date range
    bookings = await Booking.find(
        Booking.operator_id == str(operator.id),
        Booking.created_at >= start_date
    ).to_list()
    
    # Aggregate by day
    daily_sales: Dict[str, Any] = {}
    for booking in bookings:
        date_key = booking.created_at.strftime("%Y-%m-%d")
        if date_key not in daily_sales:
            daily_sales[date_key] = {
                "date": date_key,
                "bookings": 0,
                "revenue": 0.0,
            }
        
        daily_sales[date_key]["bookings"] += 1
        daily_sales[date_key]["revenue"] += booking.total_price
    
    return {
        "period_days": days,
        "daily_sales": list(daily_sales.values()),
        "total_bookings": len(bookings),
        "total_revenue": sum(b.total_price for b in bookings),
    }


@router.get("/payouts")
async def get_payouts(
    current_user: User = Depends(get_current_operator),
):
    """Get payout information"""
    
    operator = await Operator.find_one(Operator.operator_code == current_user.operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operator not found"
        )
    
    # Get transactions
    transactions = await Transaction.find(
        Transaction.operator_id == str(operator.id),
        Transaction.transaction_type == "payout"
    ).sort([("created_at", DESCENDING)]).to_list()
    
    total_payout = sum(t.amount for t in transactions)
    
    return {
        "operator": {
            "name": operator.name,
            "commission_percentage": operator.commission_percentage,
            "subaccount_code": operator.paystack_subaccount_code,
        },
        "payouts": [
            {
                "transaction_id": t.transaction_id,
                "amount": t.amount,
                "status": t.status,
                "description": t.description,
                "created_at": t.created_at,
            }
            for t in transactions
        ],
        "total_payout": total_payout,
    }
