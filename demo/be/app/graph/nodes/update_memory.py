from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.graph.state import CoachState
from app.llm.base import BaseLLMClient
from app.models import LongTermMemory
from app.repositories.memory_repository import MemoryRepository


def update_memory(state: CoachState, db: Session, llm: BaseLLMClient) -> dict:
    settings = get_settings()
    if not settings.enable_memory_update:
        return {}
    repo = MemoryRepository(db)
    extracted = llm.extract_memory_sync(
        state["user_message"],
        state.get("final_answer", ""),
        {"user_id": state["user_id"]},
    )
    for item in extracted:
        repo.create(
            LongTermMemory(
                user_id=state["user_id"],
                memory_type=item.get("memory_type", "preference"),
                content=item["content"],
                source_type="conversation",
                source_id=state.get("assistant_message_id"),
                confidence=item.get("confidence", 0.7),
            )
        )
    trace = dict(state.get("trace") or {})
    trace["update_memory"] = {"created": len(extracted)}
    return {"trace": trace}
