from sqlalchemy.orm import Session

from app.graph.state import CoachState
from app.rag.memory_index import MemoryIndexService
from app.repositories.user_repository import UserRepository


def retrieve_memory(state: CoachState, db: Session) -> dict:
    user_repo = UserRepository(db)
    sql_memories = user_repo.list_active_memories(state["user_id"], limit=10)
    memory_items = [
        {
            "memory_type": m.memory_type,
            "content": m.content,
            "confidence": m.confidence,
        }
        for m in sql_memories
    ]
    index = MemoryIndexService(db)
    retrieved = index.query(state["user_id"], state["user_message"], top_k=5)
    for r in retrieved:
        if r.content not in [x["content"] for x in memory_items]:
            memory_items.append(
                {"memory_type": "retrieved", "content": r.content, "confidence": r.score}
            )
    trace = dict(state.get("trace") or {})
    trace["retrieve_memory"] = {"count": len(memory_items)}
    return {"long_term_memories": memory_items, "trace": trace}
