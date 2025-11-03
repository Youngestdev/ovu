"""
Paystack payment service with split settlement support
"""
import httpx
import hmac
import hashlib
import logging
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.models.payment import SplitConfig

logger = logging.getLogger(__name__)


class PaystackService:
    """Paystack payment integration"""
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"
        # Paystack uses the same API endpoint for both test and live keys
        # The environment is determined by the secret key prefix (sk_test_ or sk_live_)
        
    async def initialize_transaction(
        self,
        email: str,
        amount: float,
        reference: str,
        callback_url: Optional[str] = None,
        split_config: Optional[List[SplitConfig]] = None,
    ) -> Dict[str, Any]:
        """Initialize a payment transaction"""
        
        # Amount in kobo (Paystack uses kobo for NGN)
        amount_kobo = int(amount * 100)
        
        if settings.is_development:
            logger.info(f"[DEV] Initializing payment: {reference} for {email} - Amount: NGN {amount}")
        
        payload = {
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
        }
        
        if callback_url:
            payload["callback_url"] = callback_url
        
        # Add split configuration for settlement
        if split_config:
            subaccounts = []
            for split in split_config:
                subaccounts.append({
                    "subaccount": split.subaccount_code,
                    "share": int(split.share_percentage) if not split.share_amount else int(split.share_amount * 100),
                })
            payload["subaccount"] = subaccounts[0]["subaccount"] if len(subaccounts) == 1 else None
            if len(subaccounts) > 1:
                payload["split"] = {"type": "percentage", "subaccounts": subaccounts}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/transaction/initialize",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if settings.is_development:
                        logger.info(f"[DEV] Payment initialized successfully: {reference}")
                    return {
                        "status": "success",
                        "authorization_url": data["data"]["authorization_url"],
                        "access_code": data["data"]["access_code"],
                        "reference": data["data"]["reference"],
                    }
                else:
                    error_msg = response.json().get("message", "Payment initialization failed")
                    if settings.is_development:
                        logger.error(f"[DEV] Payment initialization failed: {error_msg}")
                    return {
                        "status": "error",
                        "message": error_msg,
                    }
            except Exception as e:
                error_msg = str(e)
                if settings.is_development:
                    logger.error(f"[DEV] Error initializing payment: {error_msg}")
                else:
                    logger.error(f"Error initializing payment for reference {reference}")
                return {
                    "status": "error",
                    "message": error_msg if settings.is_development else "Payment initialization failed",
                }
    
    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a payment transaction"""
        
        if settings.is_development:
            logger.info(f"[DEV] Verifying transaction: {reference}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/transaction/verify/{reference}",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if settings.is_development:
                        logger.info(f"[DEV] Transaction verified successfully: {reference}")
                    return {
                        "status": "success",
                        "data": data["data"],
                    }
                else:
                    if settings.is_development:
                        logger.error(f"[DEV] Transaction verification failed: {reference}")
                    return {
                        "status": "error",
                        "message": "Verification failed",
                    }
            except Exception as e:
                error_msg = str(e)
                if settings.is_development:
                    logger.error(f"[DEV] Error verifying payment: {error_msg}")
                else:
                    logger.error(f"Error verifying payment for reference {reference}")
                return {
                    "status": "error",
                    "message": error_msg if settings.is_development else "Verification failed",
                }
    
    async def create_subaccount(self, operator_data: dict) -> Dict[str, Any]:
        """Create a subaccount for an operator"""
        
        if settings.is_development:
            logger.info(f"[DEV] Creating subaccount for: {operator_data.get('business_name')}")
        
        payload = {
            "business_name": operator_data["business_name"],
            "settlement_bank": operator_data["bank_code"],
            "account_number": operator_data["account_number"],
            "percentage_charge": operator_data.get("percentage_charge", 10.0),
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/subaccount",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    if settings.is_development:
                        logger.info(f"[DEV] Subaccount created: {data['data']['subaccount_code']}")
                    return {
                        "status": "success",
                        "subaccount_code": data["data"]["subaccount_code"],
                    }
                else:
                    error_msg = response.json().get("message", "Subaccount creation failed")
                    if settings.is_development:
                        logger.error(f"[DEV] Subaccount creation failed: {error_msg}")
                    return {
                        "status": "error",
                        "message": error_msg,
                    }
            except Exception as e:
                error_msg = str(e)
                if settings.is_development:
                    logger.error(f"[DEV] Error creating subaccount: {error_msg}")
                else:
                    logger.error(f"Error creating subaccount for business: {operator_data.get('business_name', 'unknown')}")
                return {
                    "status": "error",
                    "message": error_msg if settings.is_development else "Subaccount creation failed",
                }
    
    async def initiate_refund(self, reference: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Initiate a refund"""
        
        if settings.is_development:
            logger.info(f"[DEV] Initiating refund for: {reference}")
        
        payload = {
            "transaction": reference,
        }
        
        if amount:
            payload["amount"] = int(amount * 100)  # Convert to kobo
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/refund",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if settings.is_development:
                        logger.info(f"[DEV] Refund initiated successfully: {reference}")
                    return {
                        "status": "success",
                        "data": data["data"],
                    }
                else:
                    error_msg = response.json().get("message", "Refund failed")
                    if settings.is_development:
                        logger.error(f"[DEV] Refund failed: {error_msg}")
                    return {
                        "status": "error",
                        "message": error_msg,
                    }
            except Exception as e:
                error_msg = str(e)
                if settings.is_development:
                    logger.error(f"[DEV] Error initiating refund: {error_msg}")
                else:
                    logger.error(f"Error initiating refund for reference {reference}")
                return {
                    "status": "error",
                    "message": error_msg if settings.is_development else "Refund failed",
                }
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        
        webhook_secret = settings.PAYSTACK_WEBHOOK_SECRET
        
        computed_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
