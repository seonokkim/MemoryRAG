from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EvalLog, PromptVersion


class EvalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_eval(self, log: EvalLog) -> EvalLog:
        self.db.add(log)
        self.db.flush()
        return log

    def latest_for_conversation(self, conversation_id: int) -> EvalLog | None:
        stmt = (
            select(EvalLog)
            .where(EvalLog.conversation_id == conversation_id)
            .order_by(EvalLog.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def list_prompt_versions(self) -> list[PromptVersion]:
        stmt = select(PromptVersion).order_by(PromptVersion.created_at.desc())
        return list(self.db.scalars(stmt).all())
