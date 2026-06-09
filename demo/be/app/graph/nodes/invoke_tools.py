from sqlalchemy.orm import Session

from app.agents.tools import run_allowed_tools
from app.core.config import get_settings
from app.graph.state import CoachState
from app.graph.trace_utils import append_trace


def invoke_tools(state: CoachState, db: Session) -> dict:
    settings = get_settings()
    if not settings.enable_agent_tools:
        return append_trace(state, "invoke_tools", {"skipped": True, "tools_called": []})

    question_type = state.get("question_type", "unclear")
    query = state.get("rewritten_query") or state["user_message"]
    results = run_allowed_tools(
        db,
        user_id=state["user_id"],
        question_type=question_type,
        query=query,
    )
    return {
        "tool_results": results,
        **append_trace(
            state,
            "invoke_tools",
            {"tools_called": list(results.keys()), "question_type": question_type},
        ),
    }
