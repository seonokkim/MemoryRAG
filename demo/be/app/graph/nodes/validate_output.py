from pydantic import ValidationError

from app.graph.state import CoachState
from app.schemas.coach import StructuredCoachingOutput


def validate_output(state: CoachState) -> dict:
    raw = state.get("structured_output")
    try:
        if isinstance(raw, StructuredCoachingOutput):
            validated = raw
        else:
            validated = StructuredCoachingOutput.model_validate(raw)
    except ValidationError:
        return {
            "failure_type": "invalid_structured_output",
            "guardrail_status": "failed",
        }
    trace = dict(state.get("trace") or {})
    trace["validate_output"] = {"ok": True}
    return {"structured_output": validated, "trace": trace}
