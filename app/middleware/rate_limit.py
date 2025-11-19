"""
Rate limiting middleware for partner API
"""
import time
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from redis import Redis
from app.core.config import settings
from app.models.partner import Partner
from app.models.api_key import APIKey
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter for partner API"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis = Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
            self.enabled = True
            logger.info("Rate limiter initialized with Redis")
        except Exception as e:
            logger.warning(f"Redis not available, rate limiting disabled: {e}")
            self.redis = None
            self.enabled = False
    
    def _get_current_window(self) -> int:
        """Get current time window (minute)"""
        return int(time.time() / 60)
    
    def _get_current_day(self) -> str:
        """Get current day (YYYY-MM-DD)"""
        return time.strftime("%Y-%m-%d")
    
    def check_rate_limit(
        self,
        partner_id: str,
        api_key_id: Optional[str],
        limit_per_minute: int,
        limit_per_day: int
    ) -> Tuple[bool, dict]:
        """
        Check if request is within rate limits
        
        Returns: (allowed, rate_limit_info)
        """
        if not self.enabled:
            # If Redis is not available, allow all requests
            return True, {
                "limit_per_minute": limit_per_minute,
                "remaining_per_minute": limit_per_minute,
                "limit_per_day": limit_per_day,
                "remaining_per_day": limit_per_day,
                "reset_minute": int(time.time()) + 60,
                "reset_day": int(time.time()) + 86400
            }
        
        current_window = self._get_current_window()
        current_day = self._get_current_day()
        
        # Keys for tracking
        minute_key = f"rate_limit:partner:{partner_id}:minute:{current_window}"
        day_key = f"rate_limit:partner:{partner_id}:day:{current_day}"
        
        # If API key is provided, also track per-key limits
        if api_key_id:
            minute_key = f"rate_limit:api_key:{api_key_id}:minute:{current_window}"
            day_key = f"rate_limit:api_key:{api_key_id}:day:{current_day}"
        
        try:
            # Get current counts
            minute_count = self.redis.get(minute_key)
            day_count = self.redis.get(day_key)
            
            minute_count = int(minute_count) if minute_count else 0
            day_count = int(day_count) if day_count else 0
            
            # Check limits
            if minute_count >= limit_per_minute:
                return False, {
                    "limit_per_minute": limit_per_minute,
                    "remaining_per_minute": 0,
                    "limit_per_day": limit_per_day,
                    "remaining_per_day": max(0, limit_per_day - day_count),
                    "reset_minute": (current_window + 1) * 60,
                    "reset_day": int(time.time()) + 86400
                }
            
            if day_count >= limit_per_day:
                return False, {
                    "limit_per_minute": limit_per_minute,
                    "remaining_per_minute": max(0, limit_per_minute - minute_count),
                    "limit_per_day": limit_per_day,
                    "remaining_per_day": 0,
                    "reset_minute": (current_window + 1) * 60,
                    "reset_day": int(time.time()) + 86400
                }
            
            # Increment counters
            pipe = self.redis.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 120)  # Keep for 2 minutes
            pipe.incr(day_key)
            pipe.expire(day_key, 172800)  # Keep for 2 days
            pipe.execute()
            
            # Return success with rate limit info
            return True, {
                "limit_per_minute": limit_per_minute,
                "remaining_per_minute": limit_per_minute - minute_count - 1,
                "limit_per_day": limit_per_day,
                "remaining_per_day": limit_per_day - day_count - 1,
                "reset_minute": (current_window + 1) * 60,
                "reset_day": int(time.time()) + 86400
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}", exc_info=True)
            # On error, allow the request
            return True, {
                "limit_per_minute": limit_per_minute,
                "remaining_per_minute": limit_per_minute,
                "limit_per_day": limit_per_day,
                "remaining_per_day": limit_per_day,
                "reset_minute": int(time.time()) + 60,
                "reset_day": int(time.time()) + 86400
            }
    
    async def check_partner_rate_limit(
        self,
        request: Request,
        partner: Partner,
        api_key: Optional[APIKey] = None
    ) -> None:
        """
        Check rate limit and add headers to response
        Raises HTTPException if rate limit exceeded
        """
        # Determine limits (API key limits override partner limits)
        limit_per_minute = partner.rate_limit_per_minute
        limit_per_day = partner.rate_limit_per_day
        
        api_key_id = None
        if api_key:
            api_key_id = api_key.key_id
            if api_key.rate_limit_per_minute:
                limit_per_minute = api_key.rate_limit_per_minute
        
        # Check rate limit
        allowed, rate_info = self.check_rate_limit(
            partner_id=str(partner.id),
            api_key_id=api_key_id,
            limit_per_minute=limit_per_minute,
            limit_per_day=limit_per_day
        )
        
        # Store rate limit info in request state for response headers
        request.state.rate_limit_info = rate_info
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for partner {partner.partner_code} "
                f"(API key: {api_key_id or 'legacy'})"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit-Minute": str(rate_info["limit_per_minute"]),
                    "X-RateLimit-Remaining-Minute": str(rate_info["remaining_per_minute"]),
                    "X-RateLimit-Limit-Day": str(rate_info["limit_per_day"]),
                    "X-RateLimit-Remaining-Day": str(rate_info["remaining_per_day"]),
                    "X-RateLimit-Reset-Minute": str(rate_info["reset_minute"]),
                    "X-RateLimit-Reset-Day": str(rate_info["reset_day"]),
                    "Retry-After": str(rate_info["reset_minute"] - int(time.time()))
                }
            )
    
    def get_usage_stats(self, partner_id: str, days: int = 30) -> dict:
        """Get usage statistics for a partner"""
        if not self.enabled:
            return {
                "total_requests": 0,
                "daily_breakdown": []
            }
        
        try:
            stats = {
                "total_requests": 0,
                "daily_breakdown": []
            }
            
            # Get daily stats for the past N days
            for i in range(days):
                day = time.strftime("%Y-%m-%d", time.localtime(time.time() - (i * 86400)))
                day_key = f"rate_limit:partner:{partner_id}:day:{day}"
                count = self.redis.get(day_key)
                count = int(count) if count else 0
                
                stats["daily_breakdown"].append({
                    "date": day,
                    "requests": count
                })
                stats["total_requests"] += count
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}", exc_info=True)
            return {
                "total_requests": 0,
                "daily_breakdown": []
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def add_rate_limit_headers(request: Request, call_next):
    """Middleware to add rate limit headers to all responses"""
    response = await call_next(request)
    
    # Add rate limit headers if available
    if hasattr(request.state, "rate_limit_info"):
        rate_info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit-Minute"] = str(rate_info["limit_per_minute"])
        response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["remaining_per_minute"])
        response.headers["X-RateLimit-Limit-Day"] = str(rate_info["limit_per_day"])
        response.headers["X-RateLimit-Remaining-Day"] = str(rate_info["remaining_per_day"])
        response.headers["X-RateLimit-Reset-Minute"] = str(rate_info["reset_minute"])
        response.headers["X-RateLimit-Reset-Day"] = str(rate_info["reset_day"])
    
    return response
