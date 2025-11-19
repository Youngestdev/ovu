"""
Webhook service for partner notifications
"""
import asyncio
import httpx
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.partner import Partner, WebhookEvent
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for webhook delivery and management"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    async def send_webhook(
        partner: Partner,
        event_type: WebhookEvent,
        payload: Dict[str, Any],
        max_retries: int = 3
    ) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Send webhook to partner
        Returns: (success, status_code, error_message)
        """
        if not partner.webhook_url:
            logger.warning(f"Partner {partner.partner_code} has no webhook URL configured")
            return False, None, "No webhook URL configured"
        
        if event_type not in partner.webhook_events:
            logger.debug(f"Event {event_type} not subscribed by partner {partner.partner_code}")
            return False, None, "Event not subscribed"
        
        # Prepare webhook payload
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "partner_code": partner.partner_code,
            "data": payload
        }
        
        payload_str = json.dumps(webhook_payload)
        
        # Generate signature if secret is configured
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Ovu-Webhook/1.0"
        }
        
        if partner.webhook_secret:
            signature = WebhookService.generate_signature(
                payload_str,
                partner.webhook_secret
            )
            headers["X-Ovu-Signature"] = signature
        
        # Send webhook with retries
        last_error = None
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(
                        partner.webhook_url,
                        content=payload_str,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201, 202, 204]:
                        logger.info(
                            f"Webhook delivered to {partner.partner_code} "
                            f"for event {event_type}"
                        )
                        return True, response.status_code, None
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                        logger.warning(
                            f"Webhook delivery failed (attempt {attempt + 1}/{max_retries}): "
                            f"{last_error}"
                        )
                
                except httpx.TimeoutException:
                    last_error = "Request timeout"
                    logger.warning(
                        f"Webhook timeout (attempt {attempt + 1}/{max_retries}) "
                        f"for partner {partner.partner_code}"
                    )
                
                except Exception as e:
                    last_error = str(e)
                    logger.error(
                        f"Webhook error (attempt {attempt + 1}/{max_retries}): {e}",
                        exc_info=True
                    )
                
                # Wait before retry (exponential backoff)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        logger.error(
            f"Webhook delivery failed after {max_retries} attempts "
            f"for partner {partner.partner_code}: {last_error}"
        )
        return False, None, last_error
    
    @staticmethod
    async def test_webhook(
        partner: Partner,
        event_type: WebhookEvent = WebhookEvent.BOOKING_CREATED
    ) -> tuple[bool, Optional[int], Optional[float], Optional[str]]:
        """
        Test webhook configuration
        Returns: (success, status_code, response_time_ms, error_message)
        """
        if not partner.webhook_url:
            return False, None, None, "No webhook URL configured"
        
        # Prepare test payload
        test_payload = {
            "test": True,
            "message": "This is a test webhook from Ovu Transport Aggregator",
            "booking_reference": "TEST-WEBHOOK-001",
            "status": "confirmed"
        }
        
        start_time = datetime.utcnow()
        
        success, status_code, error = await WebhookService.send_webhook(
            partner=partner,
            event_type=event_type,
            payload=test_payload,
            max_retries=1  # Only one attempt for tests
        )
        
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return success, status_code, response_time_ms, error
    
    @staticmethod
    async def notify_booking_created(partner: Partner, booking_data: Dict[str, Any]):
        """Send booking created webhook"""
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CREATED,
            payload=booking_data
        )
    
    @staticmethod
    async def notify_booking_confirmed(partner: Partner, booking_data: Dict[str, Any]):
        """Send booking confirmed webhook"""
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CONFIRMED,
            payload=booking_data
        )
    
    @staticmethod
    async def notify_booking_cancelled(partner: Partner, booking_data: Dict[str, Any]):
        """Send booking cancelled webhook"""
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.BOOKING_CANCELLED,
            payload=booking_data
        )
    
    @staticmethod
    async def notify_payment_success(partner: Partner, payment_data: Dict[str, Any]):
        """Send payment success webhook"""
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.PAYMENT_SUCCESS,
            payload=payment_data
        )
    
    @staticmethod
    async def notify_payment_failed(partner: Partner, payment_data: Dict[str, Any]):
        """Send payment failed webhook"""
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.PAYMENT_FAILED,
            payload=payment_data
        )
    
    @staticmethod
    async def notify_ticket_generated(partner: Partner, ticket_data: Dict[str, Any]):
        """Send ticket generated webhook"""
        await WebhookService.send_webhook(
            partner=partner,
            event_type=WebhookEvent.TICKET_GENERATED,
            payload=ticket_data
        )
