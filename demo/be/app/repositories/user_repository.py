from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import LongTermMemory, User, UserProfile


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_profile(self, user_id: int) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        return self.db.scalar(stmt)

    def get_user_with_profile(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.profile))
            .where(User.id == user_id)
        )
        return self.db.scalar(stmt)

    def list_active_memories(self, user_id: int, limit: int = 20) -> list[LongTermMemory]:
        stmt = (
            select(LongTermMemory)
            .where(
                LongTermMemory.user_id == user_id,
                LongTermMemory.is_active.is_(True),
            )
            .order_by(LongTermMemory.updated_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
