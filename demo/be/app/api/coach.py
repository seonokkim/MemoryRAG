from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.coach import CoachChatRequest, CoachChatResponse
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["coach"])


@router.post("/chat", response_model=CoachChatResponse)
async def coach_chat(
    payload: CoachChatRequest, db: Session = Depends(get_db)
) -> CoachChatResponse:
    return await CoachService(db).chat(payload)
