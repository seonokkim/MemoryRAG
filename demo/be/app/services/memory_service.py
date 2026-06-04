from app.repositories.user_repository import UserRepository
from app.schemas.memory import MemoryItem
from sqlalchemy.orm import Session


class MemoryService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def list_for_user(self, user_id: int) -> list[MemoryItem]:
        memories = self.repo.list_active_memories(user_id)
        return [MemoryItem.model_validate(m) for m in memories]
