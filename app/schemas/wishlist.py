"""
Deprecated: Wishlist schemas shim for backward compatibility.
Prefer importing from app.schemas.waitlist.
"""
from app.schemas.waitlist import (
    WaitlistSubscribeRequest as WishlistSubscribeRequest,
    WaitlistSubscribeResponse as WishlistSubscribeResponse,
)
