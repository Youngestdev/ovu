"""
Deprecated: Wishlist routes shim for backward compatibility.
Re-export the waitlist router so existing imports continue working.
"""
from app.routes.waitlist import router  # noqa: F401
