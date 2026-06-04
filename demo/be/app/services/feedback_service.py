from app.models import FeedbackLog
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from sqlalchemy.orm import Session


class FeedbackService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FeedbackRepository(db)

    def create(self, payload: FeedbackCreate) -> FeedbackResponse:
        log = self.repo.create(
            FeedbackLog(
                user_id=payload.user_id,
                message_id=payload.message_id,
                feedback_type=payload.feedback_type,
                reason=payload.reason,
            )
        )
        self.db.commit()
        return FeedbackResponse(id=log.id)
