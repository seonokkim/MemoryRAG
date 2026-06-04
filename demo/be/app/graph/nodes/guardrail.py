from app.core.config import get_settings
from app.graph.state import CoachState


UNSAFE_TERMS = ("guarantee cure", "surgery", "prescription", "broken bone")


def guardrail(state: CoachState) -> dict:
    settings = get_settings()
    if not settings.enable_guardrail:
        return {"guardrail_status": "skipped"}

    text = (state.get("final_answer") or "").lower()
    status = "passed"
    failure = state.get("failure_type")

    if any(term in text for term in UNSAFE_TERMS):
        status = "blocked"
        failure = "unsafe_advice"
        answer = (
            "I can share general coaching guidance, but I cannot provide medical advice. "
            "Please consult a professional for injury concerns."
        )
        return {
            "guardrail_status": status,
            "failure_type": failure,
            "final_answer": answer,
        }

    if failure == "missing_swing_data" and state.get("question_type") == "swing_diagnosis":
        return {
            "guardrail_status": "fallback",
            "failure_type": failure,
            "final_answer": (
                "I need at least one swing session on file to give a reliable diagnosis. "
                "Upload a swing or create a mock session first."
            ),
        }

    if state.get("question_type") == "unclear":
        return {
            "guardrail_status": "clarify",
            "failure_type": failure or "unclear_question",
            "final_answer": (
                "Could you clarify your question? For example: slice causes, progress trend, "
                "practice plan, or your golfer profile type."
            ),
        }

    trace = dict(state.get("trace") or {})
    trace["guardrail"] = {"status": status}
    return {"guardrail_status": status, "trace": trace}
