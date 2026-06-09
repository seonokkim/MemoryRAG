from app.graph.state import CoachState
from app.llm.base import BaseLLMClient


def generate_answer(state: CoachState, llm: BaseLLMClient) -> dict:
    context = {
        "user_profile": state.get("user_profile"),
        "recent_swing_sessions": state.get("recent_swing_sessions"),
        "long_term_memories": state.get("long_term_memories"),
        "golf_knowledge_chunks": state.get("golf_knowledge_chunks"),
        "messages": state.get("messages"),
        "tool_results": state.get("tool_results"),
    }
    structured = llm.generate_structured_answer_sync(
        state["user_message"],
        state.get("question_type", "unclear"),
        context,
    )
    trace = dict(state.get("trace") or {})
    trace["generate_answer"] = {"confidence": structured.confidence}
    sources = list(structured.sources)
    return {
        "structured_output": structured,
        "final_answer": structured.summary,
        "retrieved_sources": sources,
        "trace": trace,
    }
