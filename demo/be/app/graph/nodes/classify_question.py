from app.graph.state import CoachState
from app.llm.base import BaseLLMClient


def classify_question(state: CoachState, llm: BaseLLMClient) -> dict:
    message = state["user_message"]
    qtype = llm.classify_question_sync(message, {"messages": state.get("messages", [])})
    trace = dict(state.get("trace") or {})
    trace["classify_question"] = {"question_type": qtype}
    return {"question_type": qtype, "trace": trace}
