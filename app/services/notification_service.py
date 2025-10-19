"""
Notification service for email, SMS, and WhatsApp
"""
import httpx
from typing import Optional, List
from twilio.rest import Client
from app.core.config import settings
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationService:
    """Unified notification service"""
    
    def __init__(self):
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
        """Send email notification"""
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            part1 = MIMEText(body, "plain")
            message.attach(part1)
            
            if html_body:
                part2 = MIMEText(html_body, "html")
                message.attach(part2)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS notification"""
        
        if not self.twilio_client:
            print("Twilio client not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            return message.sid is not None
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    async def send_whatsapp(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp notification"""
        
        if not self.twilio_client:
            print("Twilio client not configured")
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
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_booking_confirmation(
        self,
        email: str,
        phone: Optional[str],
        booking_reference: str,
        booking_details: dict,
    ) -> None:
        """Send booking confirmation via multiple channels"""
        
        subject = f"Booking Confirmation - {booking_reference}"
        
        body = f"""
        Dear Customer,
        
        Your booking has been confirmed!
        
        Booking Reference: {booking_reference}
        Transport Type: {booking_details.get('transport_type')}
        Route: {booking_details.get('origin')} to {booking_details.get('destination')}
        Departure: {booking_details.get('departure_date')}
        Total Amount: NGN {booking_details.get('total_price')}
        
        Thank you for choosing Ovu Transport.
        
        Best regards,
        Ovu Transport Team
        """
        
        # Send email
        await self.send_email(email, subject, body)
        
        # Send SMS if phone number is provided
        if phone:
            sms_message = f"Booking confirmed! Ref: {booking_reference}. Check your email for details."
            await self.send_sms(phone, sms_message)
    
    async def send_ticket(
        self,
        email: str,
        phone: Optional[str],
        ticket_number: str,
        ticket_url: str,
    ) -> None:
        """Send e-ticket notification"""
        
        subject = f"Your E-Ticket - {ticket_number}"
        
        body = f"""
        Dear Customer,
        
        Your e-ticket is ready!
        
        Ticket Number: {ticket_number}
        
        Download your ticket: {ticket_url}
        
        Please present this ticket at the departure terminal.
        
        Best regards,
        Ovu Transport Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Your E-Ticket is Ready!</h2>
            <p><strong>Ticket Number:</strong> {ticket_number}</p>
            <p><a href="{ticket_url}">Download Your Ticket</a></p>
            <p>Please present this ticket at the departure terminal.</p>
            <p>Best regards,<br>Ovu Transport Team</p>
        </body>
        </html>
        """
        
        await self.send_email(email, subject, body, html_body)
        
        if phone:
            sms_message = f"Your e-ticket {ticket_number} is ready! Check your email for download link."
            await self.send_sms(phone, sms_message)
    
    async def send_payment_notification(
        self,
        email: str,
        payment_reference: str,
        amount: float,
        status: str,
    ) -> None:
        """Send payment notification"""
        
        subject = f"Payment {status.upper()} - {payment_reference}"
        
        body = f"""
        Dear Customer,
        
        Payment Status: {status.upper()}
        Payment Reference: {payment_reference}
        Amount: NGN {amount}
        
        {'Thank you for your payment!' if status == 'success' else 'Please contact support if you need assistance.'}
        
        Best regards,
        Ovu Transport Team
        """
        
        await self.send_email(email, subject, body)
