from app.graph.state import CoachState
from app.graph.trace_utils import append_trace
from app.schemas.coach import StructuredCoachingOutput


def fallback_answer(state: CoachState) -> dict:
    issue = (state.get("user_profile") or {}).get("current_main_issue") or "swing consistency"
    structured = StructuredCoachingOutput(
        summary=(
            "I could not produce a high-confidence coaching answer after retries. "
            "Here is a safe fallback based on your profile and recent context."
        ),
        cause=issue,
        fix="Focus on tempo and lower-body lead in your next practice block.",
        recommended_drill="Lower-body lead drill · 10 min",
        expected_effect="More stable impact and direction control",
        sources=["user_profile", "golf_knowledge"],
        confidence=0.55,
    )
    return {
        "structured_output": structured,
        "final_answer": structured.summary,
        "quality_status": "fallback",
        "guardrail_status": "fallback",
        "failure_type": state.get("failure_type") or "quality_fallback",
        "retrieved_sources": list(structured.sources),
        **append_trace(
            state,
            "fallback_answer",
            {
                "quality_reasons": state.get("quality_reasons", []),
                "retry_count": state.get("retry_count", 0),
            },
        ),
    }
