"""
Waitlist subscription routes
"""
from fastapi import APIRouter, status, Response
from app.schemas.waitlist import WaitlistSubscribeRequest, WaitlistSubscribeResponse
from app.models.waitlist import WaitlistSubscription


router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


@router.post("/subscribe", response_model=WaitlistSubscribeResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_waitlist(req: WaitlistSubscribeRequest, response: Response):
    """Subscribe a user to the upcoming waitlist/newsletter by name and email.
    Idempotent: if the email already exists, returns the existing subscription with 200.
    """
    existing = await WaitlistSubscription.find_one(WaitlistSubscription.email == req.email)
    if existing:
        response.status_code = status.HTTP_200_OK
        return WaitlistSubscribeResponse(
            id=str(existing.id),
            name=existing.name,
            email=existing.email,
            created_at=existing.created_at,
        )

    sub = WaitlistSubscription(name=req.name, email=req.email)
    await sub.save()  # type: ignore

    return WaitlistSubscribeResponse(
        id=str(sub.id),
        name=sub.name,
        email=sub.email,
        created_at=sub.created_at,
    )
