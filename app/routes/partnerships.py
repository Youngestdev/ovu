from fastapi import APIRouter, status, Response
from app.schemas.partner import PartnershipRequest, PartnershipResponses
from app.models.partners import PartnershipInterest
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/partnerships", tags=["Partnerships"])


@router.post("/", response_model=PartnershipResponses, status_code=status.HTTP_201_CREATED)
async def indicate_partnership_request(req: PartnershipRequest, response: Response):
    existing = await PartnershipInterest.find_one(PartnershipInterest.email == req.email)
    if existing:
        response.status_code = status.HTTP_200_OK
        return existing
    sub = PartnershipInterest(company_name=req.company_name, email=req.email, phone=req.phone, category=req.category)
    await sub.insert()  # type: ignore

    # Notify the submitter via email (best-effort)
    try:
        notifier = NotificationService()
        await notifier.send_partnership_acknowledgement(
            email=req.email,
            company_name=req.company_name,
            category=req.category,
            phone=req.phone,
        )
    except Exception as e:
        logger.error(f"Failed to send partnership acknowledgement email: {e}")

    return sub
