from app.core.config import get_settings
from app.graph.state import CoachState


def route_after_validate(state: CoachState) -> str:
    settings = get_settings()
    if settings.enable_quality_loop:
        return "evaluate_answer"
    return "guardrail"


def route_after_evaluate(state: CoachState) -> str:
    settings = get_settings()
    status = state.get("quality_status", "pass")
    if status == "fallback":
        return "fallback_answer"
    if status == "retry":
        if int(state.get("retry_count") or 0) > settings.quality_max_retries:
            return "fallback_answer"
        return "rewrite_query"
    return "guardrail"


def route_after_save_messages(state: CoachState) -> str:
    if state.get("quality_status") == "fallback":
        return "log_eval"
    return "update_memory"
