from app.graph.state import CoachState
from app.graph.trace_utils import append_trace
from app.models import Message
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.coach import StructuredCoachingOutput
from sqlalchemy.orm import Session


def save_messages(state: CoachState, db: Session) -> dict:
    repo = ConversationRepository(db)
    conv_id = state["conversation_id"]
    repo.add_message(
        Message(
            conversation_id=conv_id,
            role="user",
            content=state["user_message"],
        )
    )
    structured = state.get("structured_output")
    structured_json = None
    if isinstance(structured, StructuredCoachingOutput):
        structured_json = structured.model_dump()
    elif structured:
        structured_json = structured

    trace_payload = dict(state.get("trace") or {})
    trace_payload["llm_provider"] = state.get("llm_provider")
    trace_payload["llm_model"] = state.get("llm_model")
    trace_payload["quality_status"] = state.get("quality_status")
    trace_payload["retry_count"] = state.get("retry_count", 0)

    assistant = repo.add_message(
        Message(
            conversation_id=conv_id,
            role="assistant",
            content=state.get("final_answer", ""),
            structured_output_json=structured_json,
            retrieved_context_json={
                "sources": state.get("retrieved_sources", []),
                "trace": trace_payload,
            },
            latency_ms=state.get("latency_ms"),
        )
    )
    return {
        "assistant_message_id": assistant.id,
        **append_trace(
            state,
            "save_messages",
            {"assistant_message_id": assistant.id, "conversation_id": conv_id},
        ),
    }
