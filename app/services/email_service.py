"""
Email service using Resend
"""
import resend
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from jinja2 import Template
from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailService:
    """Email service using Resend for transactional emails"""
    
    def __init__(self):
        """Initialize Resend email service"""
        resend.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        self.templates_dir = Path(__file__).parent.parent / "templates" / "emails"
        self._template_cache: Dict[str, Template] = {}
    
    def _load_template(self, template_name: str) -> Template:
        """Load and return email template with caching"""
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.html"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Email template not found: {template_name}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # Cache the template
        self._template_cache[template_name] = template
        
        return template
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        template = self._load_template(template_name)
        
        # Add common context variables
        context.setdefault('year', datetime.now().year)
        context.setdefault('company_name', 'Ovu Transport')
        
        return template.render(**context)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        reply_to: Optional[str] = None,
    ) -> bool:
        """Send email using Resend"""
        try:
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            
            if reply_to:
                params["reply_to"] = reply_to
            
            response = resend.Emails.send(params)
            
            # Check if email was sent successfully
            return response.get("id") is not None
            
        except Exception as e:
            logger.error(f"Error sending email via Resend: {e}")
            return False
    
    async def send_welcome_email(
        self,
        to_email: str,
        first_name: str,
        dashboard_url: str = "https://ovutransport.com/dashboard",
    ) -> bool:
        """Send welcome email to new user"""
        context = {
            'first_name': first_name,
            'dashboard_url': dashboard_url,
        }
        
        html_content = self._render_template('welcome', context)
        
        return await self.send_email(
            to_email=to_email,
            subject="Welcome to Ovu Transport! 🎉",
            html_content=html_content,
        )
    
    async def send_booking_confirmation(
        self,
        to_email: str,
        customer_name: str,
        booking_reference: str,
        transport_type: str,
        origin: str,
        destination: str,
        departure_date: str,
        total_passengers: int,
        total_price: float,
        booking_url: str = "https://ovutransport.com/bookings",
    ) -> bool:
        """Send booking confirmation email"""
        context = {
            'customer_name': customer_name,
            'booking_reference': booking_reference,
            'transport_type': transport_type.capitalize(),
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'total_passengers': total_passengers,
            'total_price': f"{total_price:,.2f}",
            'booking_url': f"{booking_url}/{booking_reference}",
        }
        
        html_content = self._render_template('booking_confirmation', context)
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Booking Confirmation - {booking_reference}",
            html_content=html_content,
        )
    
    async def send_ticket(
        self,
        to_email: str,
        customer_name: str,
        ticket_number: str,
        booking_reference: str,
        origin: str,
        destination: str,
        departure_date: str,
        ticket_url: str,
    ) -> bool:
        """Send e-ticket email"""
        context = {
            'customer_name': customer_name,
            'ticket_number': ticket_number,
            'booking_reference': booking_reference,
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'ticket_url': ticket_url,
        }
        
        html_content = self._render_template('ticket', context)
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Your E-Ticket - {ticket_number}",
            html_content=html_content,
        )
    
    async def send_payment_success(
        self,
        to_email: str,
        customer_name: str,
        payment_reference: str,
        booking_reference: str,
        amount: float,
        payment_date: str,
        payment_method: str = "Card",
        booking_url: str = "https://ovutransport.com/bookings",
    ) -> bool:
        """Send payment success notification"""
        context = {
            'customer_name': customer_name,
            'payment_reference': payment_reference,
            'booking_reference': booking_reference,
            'amount': f"{amount:,.2f}",
            'payment_date': payment_date,
            'payment_method': payment_method,
            'booking_url': f"{booking_url}/{booking_reference}",
        }
        
        html_content = self._render_template('payment_success', context)
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Payment Successful - {payment_reference}",
            html_content=html_content,
        )
    
    async def send_payment_failed(
        self,
        to_email: str,
        customer_name: str,
        payment_reference: str,
        booking_reference: str,
        amount: float,
        reason: Optional[str] = None,
        retry_payment_url: str = "https://ovutransport.com/payments/retry",
    ) -> bool:
        """Send payment failed notification"""
        context = {
            'customer_name': customer_name,
            'payment_reference': payment_reference,
            'booking_reference': booking_reference,
            'amount': f"{amount:,.2f}",
            'reason': reason,
            'retry_payment_url': f"{retry_payment_url}/{booking_reference}",
        }
        
        html_content = self._render_template('payment_failed', context)
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Payment Failed - {payment_reference}",
            html_content=html_content,
        )
    
    async def send_booking_cancelled(
        self,
        to_email: str,
        customer_name: str,
        booking_reference: str,
        origin: str,
        destination: str,
        departure_date: str,
        cancellation_date: str,
        refund_amount: Optional[float] = None,
        search_url: str = "https://ovutransport.com/search",
    ) -> bool:
        """Send booking cancellation notification"""
        context = {
            'customer_name': customer_name,
            'booking_reference': booking_reference,
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'cancellation_date': cancellation_date,
            'refund_amount': f"{refund_amount:,.2f}" if refund_amount else None,
            'search_url': search_url,
        }
        
        html_content = self._render_template('booking_cancelled', context)
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Booking Cancelled - {booking_reference}",
            html_content=html_content,
        )
