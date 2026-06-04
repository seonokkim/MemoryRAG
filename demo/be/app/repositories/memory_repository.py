from app.models import LongTermMemory
from app.repositories.user_repository import UserRepository


class MemoryRepository(UserRepository):
    def create(self, memory: LongTermMemory) -> LongTermMemory:
        self.db.add(memory)
        self.db.flush()
        return memory
