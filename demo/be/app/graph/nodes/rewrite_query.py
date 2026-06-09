from app.graph.state import CoachState
from app.graph.trace_utils import append_trace


def rewrite_query(state: CoachState) -> dict:
    reasons = state.get("quality_reasons") or []
    base = state.get("rewritten_query") or state["user_message"]
    focus = ", ".join(reasons) if reasons else "improve answer quality"
    rewritten = f"{base} [retry focus: {focus}]"
    return {
        "rewritten_query": rewritten,
        **append_trace(state, "rewrite_query", {"rewritten_query": rewritten, "reasons": reasons}),
    }
