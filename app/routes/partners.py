from fastapi import APIRouter, status, Response
from app.schemas.partner import PartnershipRequest, PartnershipResponses
from app.models.partners import PartnershipInterest

router = APIRouter(prefix="/partnerships", tags=["Partnerships"])


@router.post("/signup", response_model=PartnershipResponses, status_code=status.HTTP_201_CREATED)
async def indicate_partnership_request(req: PartnershipRequest, response: Response):
    existing = await PartnershipInterest.find_one(PartnershipInterest.email == req.email)
    if existing:
        response.status_code = status.HTTP_200_OK
        return existing
    sub = PartnershipInterest(company_name=req.company_name, email=req.email, phone=req.email, category=req.category)
    await sub.insert()  # type: ignore

    return sub
