from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.graph.state import CoachState
from app.graph.trace_utils import append_trace
from app.models import EvalLog
from app.repositories.eval_repository import EvalRepository


def log_eval(state: CoachState, db: Session) -> dict:
    settings = get_settings()
    repo = EvalRepository(db)
    chunk_count = state.get("retrieved_chunk_count")
    if chunk_count is None:
        chunk_count = len(state.get("golf_knowledge_chunks") or [])
    row = repo.create_eval(
        EvalLog(
            conversation_id=state.get("conversation_id"),
            message_id=state.get("assistant_message_id"),
            workflow_name="coach_chat",
            prompt_version=state.get("prompt_version", settings.active_prompt_version),
            latency_ms=state.get("latency_ms"),
            retrieved_chunk_count=chunk_count,
            cost_estimate=0.001,
            failure_type=state.get("failure_type"),
            guardrail_status=state.get("guardrail_status"),
        )
    )
    llm_meta = {
        "llm_provider": state.get("llm_provider") or settings.llm_provider,
        "llm_model": state.get("llm_model") or "",
    }
    return append_trace(
        state,
        "log_eval",
        {
            "eval_log_id": row.id,
            "retrieved_chunk_count": chunk_count,
            "guardrail_status": state.get("guardrail_status"),
            "failure_type": state.get("failure_type"),
            "quality_status": state.get("quality_status"),
            "retry_count": state.get("retry_count", 0),
            **llm_meta,
        },
    )
