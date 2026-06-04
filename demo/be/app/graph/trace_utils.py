from typing import Any

from app.graph.state import CoachState


def append_trace(state: CoachState, node: str, payload: dict[str, Any]) -> dict[str, Any]:
    trace = dict(state.get("trace") or {})
    trace[node] = payload
    return {"trace": trace}
