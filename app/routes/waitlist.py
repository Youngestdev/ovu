"""
Waitlist subscription routes
"""
from fastapi import APIRouter, status, Response, HTTPException
from app.schemas.waitlist import WaitlistSubscribeRequest, WaitlistSubscribeResponse
from app.models.waitlist import WaitlistSubscription
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


@router.post("/subscribe", response_model=WaitlistSubscribeResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_waitlist(req: WaitlistSubscribeRequest, response: Response):
    """Subscribe a user to the upcoming waitlist/newsletter by name and email.
    Idempotent: if the email already exists, returns the existing subscription with 200.
    """
    existing = await WaitlistSubscription.find_one(WaitlistSubscription.email == req.email)
    if existing:
        # Per request: return 404 when the email has already subscribed
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already subscribed",
        )

    sub = WaitlistSubscription(name=req.name, email=req.email)
    await sub.save()  # type: ignore

    # Send acknowledgement email (best-effort)
    try:
        notifier = NotificationService()
        await notifier.send_waitlist_acknowledgement(email=sub.email, name=sub.name)
    except Exception as e:
        logger.error(f"Failed to send waitlist acknowledgement email: {e}")

    return WaitlistSubscribeResponse(
        id=str(sub.id),
        name=sub.name,
        email=sub.email,
        created_at=sub.created_at,
    )
