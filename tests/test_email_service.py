"""
Tests for email service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService


class TestEmailService:
    """Test cases for EmailService"""
    
    @pytest.fixture
    def email_service(self):
        """Create email service instance for testing"""
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.RESEND_API_KEY = "test_api_key"
            mock_settings.RESEND_FROM_EMAIL = "test@example.com"
            service = EmailService()
            return service
    
    def test_email_service_initialization(self, email_service):
        """Test email service initializes correctly"""
        assert email_service is not None
        assert email_service.from_email == "test@example.com"
    
    def test_load_template(self, email_service):
        """Test template loading"""
        template = email_service._load_template('welcome')
        assert template is not None
    
    def test_render_template(self, email_service):
        """Test template rendering"""
        context = {
            'first_name': 'John',
            'dashboard_url': 'https://example.com/dashboard',
        }
        html = email_service._render_template('welcome', context)
        assert 'John' in html
        assert 'https://example.com/dashboard' in html
    
    @pytest.mark.asyncio
    async def test_send_email(self, email_service):
        """Test sending basic email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_email(
                to_email="user@example.com",
                subject="Test Email",
                html_content="<p>Test content</p>",
            )
            
            assert result is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_welcome_email(self, email_service):
        """Test sending welcome email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_welcome_email(
                to_email="user@example.com",
                first_name="John",
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check email parameters
            call_args = mock_send.call_args[0][0]
            assert call_args["to"] == ["user@example.com"]
            assert "Welcome" in call_args["subject"]
    
    @pytest.mark.asyncio
    async def test_send_booking_confirmation(self, email_service):
        """Test sending booking confirmation email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_booking_confirmation(
                to_email="user@example.com",
                customer_name="John Doe",
                booking_reference="BKG123456",
                transport_type="flight",
                origin="Lagos",
                destination="Abuja",
                departure_date="2024-01-15 10:00",
                total_passengers=2,
                total_price=50000.0,
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check email parameters
            call_args = mock_send.call_args[0][0]
            assert "BKG123456" in call_args["subject"]
    
    @pytest.mark.asyncio
    async def test_send_ticket_email(self, email_service):
        """Test sending e-ticket email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_ticket(
                to_email="user@example.com",
                customer_name="John Doe",
                ticket_number="TKT123456",
                booking_reference="BKG123456",
                origin="Lagos",
                destination="Abuja",
                departure_date="2024-01-15 10:00",
                ticket_url="https://example.com/tickets/123",
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check email parameters
            call_args = mock_send.call_args[0][0]
            assert "TKT123456" in call_args["subject"]
    
    @pytest.mark.asyncio
    async def test_send_payment_success(self, email_service):
        """Test sending payment success email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_payment_success(
                to_email="user@example.com",
                customer_name="John Doe",
                payment_reference="PAY123456",
                booking_reference="BKG123456",
                amount=50000.0,
                payment_date="2024-01-15 10:00",
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check email parameters
            call_args = mock_send.call_args[0][0]
            assert "PAY123456" in call_args["subject"]
            assert "Successful" in call_args["subject"]
    
    @pytest.mark.asyncio
    async def test_send_payment_failed(self, email_service):
        """Test sending payment failed email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_payment_failed(
                to_email="user@example.com",
                customer_name="John Doe",
                payment_reference="PAY123456",
                booking_reference="BKG123456",
                amount=50000.0,
                reason="Insufficient funds",
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check email parameters
            call_args = mock_send.call_args[0][0]
            assert "PAY123456" in call_args["subject"]
            assert "Failed" in call_args["subject"]
    
    @pytest.mark.asyncio
    async def test_send_booking_cancelled(self, email_service):
        """Test sending booking cancelled email"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.return_value = {"id": "test_id"}
            
            result = await email_service.send_booking_cancelled(
                to_email="user@example.com",
                customer_name="John Doe",
                booking_reference="BKG123456",
                origin="Lagos",
                destination="Abuja",
                departure_date="2024-01-15 10:00",
                cancellation_date="2024-01-10 12:00",
                refund_amount=45000.0,
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check email parameters
            call_args = mock_send.call_args[0][0]
            assert "BKG123456" in call_args["subject"]
            assert "Cancelled" in call_args["subject"]
    
    @pytest.mark.asyncio
    async def test_send_email_failure(self, email_service):
        """Test handling email send failure"""
        with patch('resend.Emails.send') as mock_send:
            mock_send.side_effect = Exception("API Error")
            
            result = await email_service.send_email(
                to_email="user@example.com",
                subject="Test Email",
                html_content="<p>Test content</p>",
            )
            
            assert result is False


class TestNotificationService:
    """Test cases for NotificationService"""
    
    @pytest.fixture
    def notification_service(self):
        """Create notification service instance for testing"""
        with patch('app.services.notification_service.settings'):
            service = NotificationService()
            service.email_service = Mock()
            return service
    
    @pytest.mark.asyncio
    async def test_send_booking_confirmation(self, notification_service):
        """Test sending booking confirmation notification"""
        notification_service.email_service.send_booking_confirmation = AsyncMock(return_value=True)
        notification_service.send_sms = AsyncMock(return_value=True)
        
        await notification_service.send_booking_confirmation(
            email="user@example.com",
            phone="+2348012345678",
            booking_reference="BKG123456",
            booking_details={
                "customer_name": "John Doe",
                "transport_type": "flight",
                "origin": "Lagos",
                "destination": "Abuja",
                "departure_date": "2024-01-15 10:00",
                "total_passengers": 2,
                "total_price": 50000.0,
            }
        )
        
        notification_service.email_service.send_booking_confirmation.assert_called_once()
        notification_service.send_sms.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_payment_notification_success(self, notification_service):
        """Test sending payment success notification"""
        notification_service.email_service.send_payment_success = AsyncMock(return_value=True)
        
        await notification_service.send_payment_notification(
            email="user@example.com",
            payment_reference="PAY123456",
            amount=50000.0,
            status="success",
            booking_reference="BKG123456",
            customer_name="John Doe",
        )
        
        notification_service.email_service.send_payment_success.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_payment_notification_failed(self, notification_service):
        """Test sending payment failed notification"""
        notification_service.email_service.send_payment_failed = AsyncMock(return_value=True)
        
        await notification_service.send_payment_notification(
            email="user@example.com",
            payment_reference="PAY123456",
            amount=50000.0,
            status="failed",
            booking_reference="BKG123456",
            customer_name="John Doe",
        )
        
        notification_service.email_service.send_payment_failed.assert_called_once()
