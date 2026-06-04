from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.graph.state import CoachState
from app.graph.trace_utils import append_trace
from app.repositories.conversation_repository import ConversationRepository


def load_context(state: CoachState, db: Session) -> dict:
    settings = get_settings()
    repo = ConversationRepository(db)
    messages = []
    conv_id = state.get("conversation_id")
    if conv_id:
        for m in repo.list_messages(conv_id, limit=settings.recent_message_limit):
            messages.append({"role": m.role, "content": m.content})
    return {"messages": messages, **append_trace(state, "load_context", {"message_count": len(messages)})}
