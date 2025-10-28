"""
Rate limiting middleware
"""
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def _clean_old_requests(self, key: str, window_seconds: int):
        """Remove requests outside the time window"""
        if key not in self.requests:
            return
        
        cutoff_time = time.time() - window_seconds
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff_time
        ]
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded
        Returns (is_allowed, remaining_requests)
        """
        
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(key, window_seconds)
        
        # Initialize if key doesn't exist
        if key not in self.requests:
            self.requests[key] = []
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False, 0
        
        # Add current request
        self.requests[key].append(current_time)
        
        remaining = max_requests - len(self.requests[key])
        return True, remaining


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    is_allowed, remaining = rate_limiter.check_rate_limit(
        key=client_ip,
        max_requests=60,  # 60 requests per minute
        window_seconds=60
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
