from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import SwingAnalysisResult, SwingSession


class SwingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_recent(self, user_id: int, limit: int = 10) -> list[SwingSession]:
        stmt = (
            select(SwingSession)
            .where(SwingSession.user_id == user_id)
            .order_by(SwingSession.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_session(self, session_id: int) -> SwingSession | None:
        return self.db.get(SwingSession, session_id)

    def get_session_with_analysis(self, session_id: int) -> SwingSession | None:
        stmt = (
            select(SwingSession)
            .options(joinedload(SwingSession.analysis))
            .where(SwingSession.id == session_id)
        )
        return self.db.scalar(stmt)

    def create_session(self, session: SwingSession) -> SwingSession:
        self.db.add(session)
        self.db.flush()
        return session

    def create_analysis(self, analysis: SwingAnalysisResult) -> SwingAnalysisResult:
        self.db.add(analysis)
        self.db.flush()
        return analysis
