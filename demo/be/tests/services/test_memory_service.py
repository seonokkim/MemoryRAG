from app.services.memory_service import MemoryService
from tests.constants import DEMO_PRIORITY_ISSUE


class TestMemoryService:
    def test_list_active_memories_for_user(self, db_session, user_id: int) -> None:
        items = MemoryService(db_session).list_for_user(user_id)
        assert len(items) >= 1
        assert items[0].memory_type == "swing_issue"
        assert DEMO_PRIORITY_ISSUE in items[0].content
