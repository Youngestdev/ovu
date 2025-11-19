"""
Unit tests for webhook service
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.services.webhook_service import WebhookService
from app.models.partner import Partner, PartnerStatus, WebhookEvent


class TestWebhookService:
    """Test suite for WebhookService"""
    
    def test_generate_signature(self):
        """Test HMAC signature generation"""
        payload = '{"test": "data"}'
        secret = "test_secret_key"
        
        signature = WebhookService.generate_signature(payload, secret)
        
        # Verify signature is a hex string
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 produces 64 char hex
        assert all(c in '0123456789abcdef' for c in signature)
    
    def test_signature_consistency(self):
        """Test that same payload and secret produce same signature"""
        payload = '{"test": "data"}'
        secret = "test_secret_key"
        
        sig1 = WebhookService.generate_signature(payload, secret)
        sig2 = WebhookService.generate_signature(payload, secret)
        
        assert sig1 == sig2
    
    def test_signature_different_payloads(self):
        """Test that different payloads produce different signatures"""
        secret = "test_secret_key"
        
        sig1 = WebhookService.generate_signature('{"test": "data1"}', secret)
        sig2 = WebhookService.generate_signature('{"test": "data2"}', secret)
        
        assert sig1 != sig2
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_webhook_success(self, mock_client):
        """Test successful webhook delivery"""
        # Setup mock partner
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = "test_secret"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook
        success, status_code, error = await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"booking_id": "123"}
        )
        
        # Verify success
        assert success is True
        assert status_code == 200
        assert error is None
        
        # Verify request was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Verify URL
        assert call_args[0][0] == "https://example.com/webhook"
        
        # Verify headers include signature
        headers = call_args[1]['headers']
        assert 'X-Ovu-Signature' in headers
        assert headers['Content-Type'] == 'application/json'
        assert headers['User-Agent'] == 'Ovu-Webhook/1.0'
    
    @pytest.mark.asyncio
    async def test_send_webhook_no_url(self):
        """Test webhook when partner has no URL configured"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = None
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        
        success, status_code, error = await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"test": "data"}
        )
        
        assert success is False
        assert status_code is None
        assert error == "No webhook URL configured"
    
    @pytest.mark.asyncio
    async def test_send_webhook_event_not_subscribed(self):
        """Test webhook when event is not subscribed"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.PAYMENT_SUCCESS]  # Different event
        
        success, status_code, error = await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"test": "data"}
        )
        
        assert success is False
        assert status_code is None
        assert error == "Event not subscribed"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_webhook_http_error(self, mock_client):
        """Test webhook with HTTP error response"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = None
        
        # Setup mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        success, status_code, error = await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"test": "data"},
            max_retries=1  # Only 1 retry for testing
        )
        
        assert success is False
        assert status_code is None
        assert "HTTP 500" in error
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_webhook_with_retries(self, mock_client):
        """Test webhook retry logic"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = None
        
        # First call fails, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        mock_response_fail.text = "Service Unavailable"
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = "OK"
        
        mock_post = AsyncMock(side_effect=[mock_response_fail, mock_response_success])
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        success, status_code, error = await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"test": "data"},
            max_retries=2
        )
        
        # Should succeed on second try
        assert success is True
        assert status_code == 200
        assert error is None
        
        # Verify two attempts were made
        assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_test_webhook(self, mock_client):
        """Test webhook testing functionality"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = "test_secret"
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        success, status_code, response_time, error = await WebhookService.test_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED
        )
        
        assert success is True
        assert status_code == 200
        assert response_time is not None
        assert response_time > 0  # Should have some response time
        assert error is None
    
    @pytest.mark.asyncio
    async def test_notify_booking_created(self):
        """Test booking created notification helper"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = None  # Will fail gracefully
        partner.webhook_events = []
        
        # Should not raise exception
        await WebhookService.notify_booking_created(
            partner=partner,
            booking_data={"booking_id": "123"}
        )
    
    @pytest.mark.asyncio
    async def test_notify_payment_success(self):
        """Test payment success notification helper"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = None
        partner.webhook_events = []
        
        await WebhookService.notify_payment_success(
            partner=partner,
            payment_data={"payment_id": "456"}
        )
    
    @pytest.mark.asyncio
    async def test_notify_ticket_generated(self):
        """Test ticket generated notification helper"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = None
        partner.webhook_events = []
        
        await WebhookService.notify_ticket_generated(
            partner=partner,
            ticket_data={"ticket_id": "789"}
        )


class TestWebhookPayload:
    """Test webhook payload structure"""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_webhook_payload_structure(self, mock_client):
        """Test that webhook payload has correct structure"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = None
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        captured_payload = None
        
        async def capture_post(*args, **kwargs):
            nonlocal captured_payload
            captured_payload = kwargs.get('content')
            return mock_response
        
        mock_client.return_value.__aenter__.return_value.post = capture_post
        
        test_data = {"booking_id": "123", "status": "confirmed"}
        
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload=test_data
        )
        
        # Parse captured payload
        payload = json.loads(captured_payload)
        
        # Verify structure
        assert "event" in payload
        assert "timestamp" in payload
        assert "partner_code" in payload
        assert "data" in payload
        
        # Verify values
        assert payload["event"] == WebhookEvent.BOOKING_CREATED
        assert payload["partner_code"] == "TEST-123"
        assert payload["data"] == test_data
        
        # Verify timestamp is ISO format
        datetime.fromisoformat(payload["timestamp"])


class TestWebhookSecurity:
    """Test webhook security features"""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_signature_included_with_secret(self, mock_client):
        """Test that signature is included when secret is configured"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = "my_secret_key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"test": "data"}
        )
        
        # Get the headers from the call
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        
        assert 'X-Ovu-Signature' in headers
        assert len(headers['X-Ovu-Signature']) == 64  # SHA-256 hex
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_no_signature_without_secret(self, mock_client):
        """Test that signature is not included without secret"""
        partner = Mock(spec=Partner)
        partner.partner_code = "TEST-123"
        partner.webhook_url = "https://example.com/webhook"
        partner.webhook_events = [WebhookEvent.BOOKING_CREATED]
        partner.webhook_secret = None
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload={"test": "data"}
        )
        
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        
        assert 'X-Ovu-Signature' not in headers
