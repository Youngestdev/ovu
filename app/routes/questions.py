"""
Routes for submitting user questions
"""
from fastapi import APIRouter, status, Response
from app.schemas.question import QuestionRequest, QuestionResponse
from app.models.questions import Question
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def submit_question(req: QuestionRequest, response: Response):
    """Accept a user's question and store it in the DB"""
    q = Question(email=req.email, question=req.question, name=req.name)
    await q.insert()  # type: ignore

    return QuestionResponse(
        id=str(q.id),
        email=q.email,
        question=q.question,
        name=q.name,
        created_at=q.created_at,
    )
