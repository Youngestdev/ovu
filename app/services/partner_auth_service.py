"""
Partner authentication service
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.models.partner import Partner, PartnerStatus
from app.schemas.partner_auth import PartnerRegister
from app.services.partner_service import PartnerService
from app.core.security import create_access_token, get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)


class PartnerAuthService:
    """Service for partner authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return get_password_hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return verify_password(plain_password, hashed_password)
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate email verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def register_partner(registration_data: PartnerRegister) -> Tuple[Partner, str]:
        """
        Register a new partner
        Returns: (partner, verification_token)
        """
        # Check if email already exists
        existing = await Partner.find_one(Partner.email == registration_data.email)
        if existing:
            raise ValueError("Email already registered")
        
        # Generate partner code
        partner_code = PartnerService.generate_partner_code(registration_data.company_name)
        
        # Generate temporary API credentials (will be replaced on approval)
        temp_api_key, temp_api_secret = PartnerService.generate_api_credentials()
        
        # Generate verification token
        verification_token = PartnerAuthService.generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create partner
        partner = Partner(
            partner_code=partner_code,
            name=registration_data.name,
            email=registration_data.email,
            phone=registration_data.phone,
            website=registration_data.website,
            company_name=registration_data.company_name,
            business_type=registration_data.business_type,
            tax_id=registration_data.tax_id,
            business_description=registration_data.business_description,
            expected_monthly_volume=registration_data.expected_monthly_volume,
            password_hash=PartnerAuthService.hash_password(registration_data.password),
            email_verified=False,
            email_verification_token=verification_token,
            email_verification_expires=verification_expires,
            status=PartnerStatus.PENDING_VERIFICATION,
            api_key=temp_api_key,
            api_secret=PartnerService.hash_secret(temp_api_secret),
        )
        
        await partner.insert()
        logger.info(f"New partner registered: {partner.email}")
        
        return partner, verification_token
    
    @staticmethod
    async def verify_email(token: str) -> Partner:
        """Verify partner email"""
        partner = await Partner.find_one(
            Partner.email_verification_token == token
        )
        
        if not partner:
            raise ValueError("Invalid verification token")
        
        if partner.email_verified:
            raise ValueError("Email already verified")
        
        if partner.email_verification_expires < datetime.utcnow():
            raise ValueError("Verification token expired")
        
        # Update partner
        partner.email_verified = True
        partner.status = PartnerStatus.PENDING_APPROVAL
        partner.email_verification_token = None
        partner.email_verification_expires = None
        partner.updated_at = datetime.utcnow()
        
        await partner.save()
        logger.info(f"Email verified for partner: {partner.email}")
        
        return partner
    
    @staticmethod
    async def authenticate_partner(email: str, password: str) -> Optional[Partner]:
        """Authenticate partner with email and password"""
        partner = await Partner.find_one(Partner.email == email)
        
        if not partner:
            return None
        
        if not partner.password_hash:
            return None
        
        if not PartnerAuthService.verify_password(password, partner.password_hash):
            return None
        
        return partner
    
    @staticmethod
    def create_partner_tokens(partner: Partner) -> dict:
        """Create JWT tokens for partner"""
        # Access token (1 hour)
        access_token_expires = timedelta(hours=1)
        access_token = create_access_token(
            data={"sub": str(partner.id), "type": "partner"},
            expires_delta=access_token_expires
        )
        
        # Refresh token (7 days)
        refresh_token_expires = timedelta(days=7)
        refresh_token = create_access_token(
            data={"sub": str(partner.id), "type": "partner_refresh"},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "partner": {
                "id": str(partner.id),
                "partner_code": partner.partner_code,
                "name": partner.name,
                "email": partner.email,
                "company_name": partner.company_name,
                "status": partner.status,
                "email_verified": partner.email_verified
            }
        }
    
    @staticmethod
    async def initiate_password_reset(email: str) -> Tuple[Partner, str]:
        """Initiate password reset"""
        partner = await Partner.find_one(Partner.email == email)
        
        if not partner:
            # Don't reveal if email exists
            raise ValueError("If this email is registered, a reset link has been sent")
        
        # Generate reset token
        reset_token = PartnerAuthService.generate_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        partner.reset_token = reset_token
        partner.reset_token_expires = reset_expires
        partner.updated_at = datetime.utcnow()
        
        await partner.save()
        logger.info(f"Password reset initiated for: {partner.email}")
        
        return partner, reset_token
    
    @staticmethod
    async def reset_password(token: str, new_password: str) -> Partner:
        """Reset password with token"""
        partner = await Partner.find_one(Partner.reset_token == token)
        
        if not partner:
            raise ValueError("Invalid reset token")
        
        if partner.reset_token_expires < datetime.utcnow():
            raise ValueError("Reset token expired")
        
        # Update password
        partner.password_hash = PartnerAuthService.hash_password(new_password)
        partner.reset_token = None
        partner.reset_token_expires = None
        partner.updated_at = datetime.utcnow()
        
        await partner.save()
        logger.info(f"Password reset for: {partner.email}")
        
        return partner
    
    @staticmethod
    async def change_password(partner: Partner, current_password: str, new_password: str) -> Partner:
        """Change password (authenticated)"""
        if not partner.password_hash:
            raise ValueError("No password set for this account")
        
        if not PartnerAuthService.verify_password(current_password, partner.password_hash):
            raise ValueError("Current password is incorrect")
        
        partner.password_hash = PartnerAuthService.hash_password(new_password)
        partner.updated_at = datetime.utcnow()
        
        await partner.save()
        logger.info(f"Password changed for: {partner.email}")
        
        return partner
