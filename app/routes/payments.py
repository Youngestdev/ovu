"""
Payment routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.schemas.payment import PaymentInitiate, PaymentResponse, PaymentWebhook, RefundRequest
from app.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentProvider
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.middleware.auth import get_current_user
from app.services.payment_service import PaystackService
from app.services.notification_service import NotificationService
from app.utils.helpers import generate_reference


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initialize", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def initialize_payment(
    payment_data: PaymentInitiate,
    current_user: User = Depends(get_current_user)
):
    """Initialize a payment for a booking"""
    
    # Get booking
    booking = await Booking.get(payment_data.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user owns the booking
    if booking.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this booking"
        )
    
    # Check if booking is already paid
    if booking.status == BookingStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already paid"
        )
    
    # Generate payment reference
    payment_reference = generate_reference("PAY")
    
    # Create payment record
    payment = Payment(
        payment_reference=payment_reference,
        booking_id=str(booking.id),
        user_id=str(current_user.id),
        amount=booking.total_price,
        currency=booking.currency,
        payment_method=payment_data.payment_method,
        payment_provider=PaymentProvider.PAYSTACK,
    )
    
    await payment.save()
    
    # Initialize payment with Paystack
    paystack_service = PaystackService()
    result = await paystack_service.initialize_transaction(
        email=current_user.email,
        amount=booking.total_price,
        reference=payment_reference,
        callback_url=payment_data.callback_url,
    )
    
    if result.get("status") == "success":
        payment.provider_reference = result.get("reference")
        await payment.save()
        
        return PaymentResponse(
            payment_reference=payment.payment_reference,
            booking_id=payment.booking_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            authorization_url=result.get("authorization_url"),
        )
    else:
        payment.status = PaymentStatus.FAILED
        await payment.save()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Payment initialization failed")
        )


@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle Paystack webhooks"""
    
    # Get signature from header
    signature = request.headers.get("x-paystack-signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )
    
    # Get raw body
    body = await request.body()
    
    # Verify signature
    paystack_service = PaystackService()
    if not paystack_service.verify_webhook_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Parse webhook data
    data = await request.json()
    event = data.get("event")
    payment_data = data.get("data", {})
    
    if event == "charge.success":
        # Get payment by reference
        reference = payment_data.get("reference")
        payment = await Payment.find_one(Payment.payment_reference == reference)
        
        if payment:
            # Update payment status
            payment.status = PaymentStatus.SUCCESS
            payment.provider_reference = payment_data.get("id")
            from datetime import datetime
            payment.paid_at = datetime.utcnow()
            await payment.save()
            
            # Update booking status
            booking = await Booking.get(payment.booking_id)
            if booking:
                booking.status = BookingStatus.PAID
                await booking.save()
                
                # Get user
                user = await User.get(payment.user_id)
                
                # Send notification
                notification_service = NotificationService()
                await notification_service.send_payment_notification(
                    email=user.email,
                    payment_reference=reference,
                    amount=payment.amount,
                    status="success",
                    booking_reference=booking.booking_reference,
                    customer_name=f"{user.first_name} {user.last_name}",
                )
    
    return {"status": "success"}


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment details"""
    
    payment = await Payment.get(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if user owns the payment
    if payment.user_id != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    
    return PaymentResponse(
        payment_reference=payment.payment_reference,
        booking_id=payment.booking_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
    )


@router.post("/refund", status_code=status.HTTP_202_ACCEPTED)
async def request_refund(
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_user)
):
    """Request a refund"""
    
    # Get booking
    booking = await Booking.get(refund_data.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user owns the booking
    if booking.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to refund this booking"
        )
    
    # Get payment
    payment = await Payment.find_one(Payment.booking_id == str(booking.id))
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if payment can be refunded
    if payment.status != PaymentStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be refunded"
        )
    
    # Initiate refund
    paystack_service = PaystackService()
    result = await paystack_service.initiate_refund(
        reference=payment.provider_reference or payment.payment_reference,
        amount=refund_data.amount,
    )
    
    if result.get("status") == "success":
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        await payment.save()
        
        # Update booking status
        booking.status = BookingStatus.REFUNDED
        booking.cancellation_reason = refund_data.reason
        await booking.save()
        
        return {"message": "Refund initiated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Refund failed")
        )
