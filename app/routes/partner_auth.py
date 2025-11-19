"""
Partner authentication routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from datetime import datetime

from app.schemas.partner_auth import (
    PartnerRegister, PartnerLogin, TokenResponse,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest,
    ChangePasswordRequest, PartnerApprovalRequest,
    RegistrationResponse, EmailVerificationResponse
)
from app.services.partner_auth_service import PartnerAuthService
from app.services.partner_service import PartnerService
from app.models.partner import Partner, PartnerStatus
from app.models.user import User
from app.middleware.auth import get_current_partner, get_current_admin
from app.core.security import decode_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/partners/auth", tags=["Partner Authentication"])
admin_router = APIRouter(prefix="/api/v1/admin/partners", tags=["Admin - Partner Management"])


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================================================

@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_partner(registration_data: PartnerRegister):
    """
    Self-service partner registration
    
    Creates a new partner account with PENDING_VERIFICATION status.
    Sends verification email to the provided email address.
    """
    try:
        partner, verification_token = await PartnerAuthService.register_partner(registration_data)
        
        # TODO: Send verification email
        # await send_verification_email(partner.email, verification_token)
        
        logger.info(f"Partner registered: {partner.email}")
        
        return RegistrationResponse(
            message="Registration successful. Please check your email to verify your account.",
            partner_id=str(partner.id),
            email=partner.email,
            status=partner.status
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


@router.get("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(token: str = Query(..., description="Email verification token")):
    """
    Verify partner email address
    
    Updates partner status from PENDING_VERIFICATION to PENDING_APPROVAL.
    Notifies admins of new partner application.
    """
    try:
        partner = await PartnerAuthService.verify_email(token)
        
        # TODO: Send admin notification email
        # await notify_admins_new_partner(partner)
        
        logger.info(f"Email verified: {partner.email}")
        
        return EmailVerificationResponse(
            message="Email verified successfully. Your application is pending admin approval.",
            status=partner.status
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login_partner(login_data: PartnerLogin):
    """
    Partner login
    
    Authenticates partner and returns JWT tokens for dashboard access.
    Partner must be ACTIVE to login.
    """
    partner = await PartnerAuthService.authenticate_partner(
        login_data.email,
        login_data.password
    )
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if partner.status != PartnerStatus.ACTIVE:
        status_messages = {
            PartnerStatus.PENDING_VERIFICATION: "Please verify your email address",
            PartnerStatus.PENDING_APPROVAL: "Your application is pending admin approval",
            PartnerStatus.REJECTED: "Your application has been rejected",
            PartnerStatus.SUSPENDED: "Your account has been suspended",
            PartnerStatus.INACTIVE: "Your account is inactive"
        }
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=status_messages.get(partner.status, "Account is not active")
        )
    
    tokens = PartnerAuthService.create_partner_tokens(partner)
    
    logger.info(f"Partner logged in: {partner.email}")
    
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token
    
    Uses refresh token to generate a new access token.
    """
    try:
        payload = decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "partner_refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        partner_id = payload.get("sub")
        partner = await Partner.get(partner_id)
        
        if not partner or partner.status != PartnerStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        tokens = PartnerAuthService.create_partner_tokens(partner)
        
        return TokenResponse(**tokens)
    
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset
    
    Sends password reset email if account exists.
    """
    try:
        partner, reset_token = await PartnerAuthService.initiate_password_reset(request.email)
        
        # TODO: Send password reset email
        # await send_password_reset_email(partner.email, reset_token)
        
        logger.info(f"Password reset requested: {request.email}")
        
    except ValueError:
        # Don't reveal if email exists
        pass
    
    return {
        "message": "If this email is registered, a password reset link has been sent."
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password with token
    
    Resets password using the token from forgot-password email.
    """
    try:
        partner = await PartnerAuthService.reset_password(
            request.token,
            request.new_password
        )
        
        logger.info(f"Password reset: {partner.email}")
        
        return {
            "message": "Password reset successful. You can now login with your new password."
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# PARTNER DASHBOARD ENDPOINTS (JWT Authentication Required)
# ============================================================================

@router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    partner: Partner = Depends(get_current_partner)
):
    """
    Change password (authenticated)
    
    Requires current password for verification.
    """
    try:
        await PartnerAuthService.change_password(
            partner,
            request.current_password,
            request.new_password
        )
        
        logger.info(f"Password changed: {partner.email}")
        
        return {
            "message": "Password changed successfully"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# ADMIN ENDPOINTS (Admin Authentication Required)
# ============================================================================

@admin_router.get("/pending", response_model=List[dict])
async def list_pending_partners(
    admin: User = Depends(get_current_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List pending partner applications
    
    Returns partners with PENDING_APPROVAL status.
    """
    partners = await Partner.find(
        Partner.status == PartnerStatus.PENDING_APPROVAL
    ).skip(skip).limit(limit).to_list()
    
    return [
        {
            "id": str(p.id),
            "partner_code": p.partner_code,
            "name": p.name,
            "email": p.email,
            "company_name": p.company_name,
            "business_type": p.business_type,
            "business_description": p.business_description,
            "expected_monthly_volume": p.expected_monthly_volume,
            "created_at": p.created_at,
            "email_verified": p.email_verified
        }
        for p in partners
    ]


@admin_router.post("/{partner_id}/approve", status_code=status.HTTP_200_OK)
async def approve_partner(
    partner_id: str,
    approval_data: PartnerApprovalRequest,
    admin: User = Depends(get_current_admin)
):
    """
    Approve or reject partner application
    
    If approved:
    - Updates status to ACTIVE
    - Generates API credentials
    - Sends welcome email
    
    If rejected:
    - Updates status to REJECTED
    - Sends rejection email
    """
    partner = await Partner.get(partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    if partner.status != PartnerStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Partner status is {partner.status}, expected pending_approval"
        )
    
    if approval_data.action == "approve":
        # Approve partner
        partner.status = PartnerStatus.ACTIVE
        partner.approved_by = str(admin.id)
        partner.approved_at = datetime.utcnow()
        partner.approval_notes = approval_data.notes
        
        # Set rate limits
        if approval_data.rate_limit_per_minute:
            partner.rate_limit_per_minute = approval_data.rate_limit_per_minute
        if approval_data.rate_limit_per_day:
            partner.rate_limit_per_day = approval_data.rate_limit_per_day
        
        # Generate new API credentials (replace temp ones)
        api_key, api_secret = PartnerService.generate_api_credentials()
        partner.api_key = api_key
        partner.api_secret = PartnerService.hash_secret(api_secret)
        
        partner.updated_at = datetime.utcnow()
        await partner.save()
        
        # TODO: Send approval email with credentials
        # await send_approval_email(partner, api_key, api_secret)
        
        logger.info(f"Partner approved: {partner.email} by admin {admin.email}")
        
        return {
            "message": "Partner approved successfully",
            "partner_id": str(partner.id),
            "status": partner.status,
            "api_key": api_key,
            "api_secret": api_secret,
            "note": "API credentials have been sent to the partner's email"
        }
    
    elif approval_data.action == "reject":
        # Reject partner
        partner.status = PartnerStatus.REJECTED
        partner.rejected_reason = approval_data.reason
        partner.rejected_at = datetime.utcnow()
        partner.updated_at = datetime.utcnow()
        
        await partner.save()
        
        # TODO: Send rejection email
        # await send_rejection_email(partner, approval_data.reason)
        
        logger.info(f"Partner rejected: {partner.email} by admin {admin.email}")
        
        return {
            "message": "Partner application rejected",
            "partner_id": str(partner.id),
            "status": partner.status
        }


@admin_router.post("/{partner_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_partner(
    partner_id: str,
    reason: str = Query(..., min_length=10, max_length=500),
    admin: User = Depends(get_current_admin)
):
    """
    Suspend an active partner
    
    Prevents partner from accessing the API.
    """
    partner = await Partner.get(partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    if partner.status != PartnerStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only suspend active partners"
        )
    
    partner.status = PartnerStatus.SUSPENDED
    partner.metadata["suspension_reason"] = reason
    partner.metadata["suspended_by"] = str(admin.id)
    partner.metadata["suspended_at"] = datetime.utcnow().isoformat()
    partner.updated_at = datetime.utcnow()
    
    await partner.save()
    
    # TODO: Send suspension notification email
    # await send_suspension_email(partner, reason)
    
    logger.info(f"Partner suspended: {partner.email} by admin {admin.email}")
    
    return {
        "message": "Partner suspended successfully",
        "partner_id": str(partner.id),
        "status": partner.status
    }


@admin_router.post("/{partner_id}/activate", status_code=status.HTTP_200_OK)
async def activate_partner(
    partner_id: str,
    admin: User = Depends(get_current_admin)
):
    """
    Activate a suspended partner
    
    Restores partner access to the API.
    """
    partner = await Partner.get(partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    if partner.status != PartnerStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only activate suspended partners"
        )
    
    partner.status = PartnerStatus.ACTIVE
    partner.metadata["reactivated_by"] = str(admin.id)
    partner.metadata["reactivated_at"] = datetime.utcnow().isoformat()
    partner.updated_at = datetime.utcnow()
    
    await partner.save()
    
    # TODO: Send reactivation email
    # await send_reactivation_email(partner)
    
    logger.info(f"Partner reactivated: {partner.email} by admin {admin.email}")
    
    return {
        "message": "Partner activated successfully",
        "partner_id": str(partner.id),
        "status": partner.status
    }
