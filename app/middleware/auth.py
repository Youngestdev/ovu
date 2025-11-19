"""
Authentication middleware and dependencies
"""
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import decode_token
from app.models.user import User
from app.models.partner import Partner


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_operator(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current operator user"""
    if current_user.role not in ["operator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as operator",
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def get_current_partner(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> "Partner":
    """Get current authenticated partner from JWT token"""
    from app.models.partner import Partner, PartnerStatus
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "partner":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    partner_id = payload.get("sub")
    if not partner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    partner = await Partner.get(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Partner not found",
        )
    
    if partner.status != PartnerStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Partner account is not active",
        )
    
    return partner


async def verify_partner_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None)
) -> Partner:
    """Verify partner API key and check rate limits"""
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )
    
    # Try to find partner by legacy api_key
    partner = await Partner.find_one(Partner.api_key == x_api_key)
    api_key_doc = None
    
    # If not found, try new APIKey model
    if not partner:
        from app.models.api_key import APIKey, APIKeyStatus
        
        # In a real implementation, you'd hash the incoming key and compare
        # For now, we'll search by key_id (simplified)
        # This is a placeholder - implement proper key verification
        api_key_doc = await APIKey.find_one(
            APIKey.status == APIKeyStatus.ACTIVE
        )
        
        if api_key_doc:
            partner = await Partner.get(api_key_doc.partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    if partner.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Partner account is not active",
        )
    
    # Check rate limits
    from app.middleware.rate_limit import rate_limiter
    await rate_limiter.check_partner_rate_limit(
        request=request,
        partner=partner,
        api_key=api_key_doc
    )
    
    # Update usage tracking
    partner.total_requests += 1
    from datetime import datetime
    partner.last_request_at = datetime.utcnow()
    await partner.save()
    
    # Update API key usage if applicable
    if api_key_doc:
        api_key_doc.total_requests += 1
        api_key_doc.last_used_at = datetime.utcnow()
        await api_key_doc.save()
    
    return partner
