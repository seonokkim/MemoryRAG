from app.core.config import get_settings
from app.graph.state import CoachState
from app.graph.trace_utils import append_trace
from app.schemas.coach import StructuredCoachingOutput

UNSAFE_TERMS = ("surgery", "prescription", "broken bone", "guarantee cure")
REQUIRED_FIELDS = ("summary", "cause", "fix", "recommended_drill")


def _structured_dict(state: CoachState) -> dict:
    raw = state.get("structured_output")
    if isinstance(raw, StructuredCoachingOutput):
        return raw.model_dump()
    if isinstance(raw, dict):
        return raw
    return {}


def evaluate_answer(state: CoachState) -> dict:
    settings = get_settings()
    if not settings.enable_quality_loop:
        return append_trace(state, "evaluate_answer", {"quality_status": "pass", "skipped": True})

    reasons: list[str] = []
    data = _structured_dict(state)
    retry_count = int(state.get("retry_count") or 0)

    if state.get("failure_type") == "invalid_structured_output":
        reasons.append("invalid_structured_output")
    else:
        for field in REQUIRED_FIELDS:
            if not str(data.get(field, "")).strip():
                reasons.append(f"missing_{field}")

        confidence = float(data.get("confidence") or 0.0)
        if confidence < settings.quality_confidence_threshold:
            reasons.append("low_confidence")

        text = " ".join(
            str(data.get(k, "")) for k in ("summary", "cause", "fix", "recommended_drill")
        ).lower()
        if any(term in text for term in UNSAFE_TERMS):
            reasons.append("unsafe_medical_language")

        sources = state.get("retrieved_sources") or data.get("sources") or []
        has_context = bool(sources) or bool(state.get("recent_swing_sessions"))
        if not has_context and state.get("question_type") != "unclear":
            reasons.append("weak_grounding")

        drill = str(data.get("recommended_drill", "")).strip()
        fix = str(data.get("fix", "")).strip()
        if not drill and not fix:
            reasons.append("no_actionable_next_step")

    if not reasons:
        return {
            "quality_status": "pass",
            "quality_reasons": [],
            "retry_count": retry_count,
            **append_trace(
                state,
                "evaluate_answer",
                {"quality_status": "pass", "quality_reasons": [], "retry_count": retry_count},
            ),
        }

    next_retry = retry_count + 1
    if next_retry <= settings.quality_max_retries:
        return {
            "quality_status": "retry",
            "quality_reasons": reasons,
            "retry_count": next_retry,
            **append_trace(
                state,
                "evaluate_answer",
                {
                    "quality_status": "retry",
                    "quality_reasons": reasons,
                    "retry_count": next_retry,
                },
            ),
        }

    return {
        "quality_status": "fallback",
        "quality_reasons": reasons,
        "retry_count": retry_count,
        **append_trace(
            state,
            "evaluate_answer",
            {
                "quality_status": "fallback",
                "quality_reasons": reasons,
                "retry_count": retry_count,
            },
        ),
    }
