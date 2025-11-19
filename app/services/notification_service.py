"""
Notification service for email, SMS, and WhatsApp
"""
import logging
import httpx
from typing import Optional, List
from twilio.rest import Client
from app.core.config import settings
from app.services.email_service import EmailService
from datetime import datetime


logger = logging.getLogger(__name__)


class NotificationService:
    """Unified notification service"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send email notification using Resend"""
        
        try:
            # Use HTML body if provided, otherwise use plain text
            html_content = html_body if html_body else f"<pre>{body}</pre>"
            
            return await self.email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
            )
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS notification"""
        
        if not self.twilio_client:
            logger.warning("Twilio client not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            return message.sid is not None
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def send_whatsapp(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp notification"""
        
        if not self.twilio_client:
            logger.warning("Twilio client not configured")
            return False
        
        try:
            # Format phone number for WhatsApp
            whatsapp_to = f"whatsapp:{to_phone}"
            
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=whatsapp_to
            )
            
            return message.sid is not None
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_booking_confirmation(
        self,
        email: str,
        phone: Optional[str],
        booking_reference: str,
        booking_details: dict,
    ) -> None:
        """Send booking confirmation via multiple channels"""
        
        # Send email using new template-based service
        await self.email_service.send_booking_confirmation(
            to_email=email,
            customer_name=booking_details.get('customer_name', 'Customer'),
            booking_reference=booking_reference,
            transport_type=booking_details.get('transport_type', ''),
            origin=booking_details.get('origin', ''),
            destination=booking_details.get('destination', ''),
            departure_date=booking_details.get('departure_date', ''),
            total_passengers=booking_details.get('total_passengers', 1),
            total_price=booking_details.get('total_price', 0),
        )
        
        # Send SMS if phone number is provided
        if phone:
            sms_message = f"Booking confirmed! Ref: {booking_reference}. Check your email for details."
            await self.send_sms(phone, sms_message)

    async def send_waitlist_acknowledgement(self, email: str, name: Optional[str] = None) -> None:
        """Notify a user who subscribed to the waitlist"""
        await self.email_service.send_waitlist_subscription(
            to_email=email,
            name=name,
        )

    async def send_partnership_acknowledgement(self, email: str, company_name: str, category: str, phone: Optional[str] = None) -> None:
        """Notify a user/company who submitted partnership interest"""
        await self.email_service.send_partnership_acknowledgement(
            to_email=email,
            company_name=company_name,
            category=category,
            phone=phone,
        )
    
    async def send_ticket(
        self,
        email: str,
        phone: Optional[str],
        ticket_number: str,
        ticket_url: str,
        booking_details: Optional[dict] = None,
    ) -> None:
        """Send e-ticket notification"""
        
        if booking_details is None:
            booking_details = {}
        
        await self.email_service.send_ticket(
            to_email=email,
            customer_name=booking_details.get('customer_name', 'Customer'),
            ticket_number=ticket_number,
            booking_reference=booking_details.get('booking_reference', ''),
            origin=booking_details.get('origin', ''),
            destination=booking_details.get('destination', ''),
            departure_date=booking_details.get('departure_date', ''),
            ticket_url=ticket_url,
        )
        
        if phone:
            sms_message = f"Your e-ticket {ticket_number} is ready! Check your email for download link."
            await self.send_sms(phone, sms_message)
    
    async def send_payment_notification(
        self,
        email: str,
        payment_reference: str,
        amount: float,
        status: str,
        booking_reference: str = "",
        customer_name: str = "Customer",
    ) -> None:
        """Send payment notification"""
        
        if status == "success":
            await self.email_service.send_payment_success(
                to_email=email,
                customer_name=customer_name,
                payment_reference=payment_reference,
                booking_reference=booking_reference,
                amount=amount,
                payment_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )
        else:
            await self.email_service.send_payment_failed(
                to_email=email,
                customer_name=customer_name,
                payment_reference=payment_reference,
                booking_reference=booking_reference,
                amount=amount,
            )
