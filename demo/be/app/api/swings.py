from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.swing import SwingAnalysisResponse, SwingSessionCreate, SwingSessionItem
from app.services.swing_service import SwingService

router = APIRouter(tags=["swings"])


@router.get("/users/{user_id}/swing-sessions", response_model=list[SwingSessionItem])
def list_swing_sessions(
    user_id: int, db: Session = Depends(get_db)
) -> list[SwingSessionItem]:
    return SwingService(db).list_sessions(user_id)


@router.post("/users/{user_id}/swing-sessions", response_model=SwingSessionItem)
def create_swing_session(
    user_id: int,
    payload: SwingSessionCreate,
    db: Session = Depends(get_db),
) -> SwingSessionItem:
    session, _ = SwingService(db).create_mock_session(user_id, payload)
    return session


@router.get("/swing-sessions/{session_id}/analysis", response_model=SwingAnalysisResponse)
def get_swing_analysis(
    session_id: int, db: Session = Depends(get_db)
) -> SwingAnalysisResponse:
    return SwingService(db).get_analysis(session_id)
