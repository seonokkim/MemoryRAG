from functools import partial

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.observability import build_coach_workflow_invoke_config
from app.graph.nodes.classify_question import classify_question
from app.graph.nodes.evaluate_answer import evaluate_answer
from app.graph.nodes.fallback_answer import fallback_answer
from app.graph.nodes.generate_answer import generate_answer
from app.graph.nodes.guardrail import guardrail
from app.graph.nodes.invoke_tools import invoke_tools
from app.graph.nodes.load_context import load_context
from app.graph.nodes.log_eval import log_eval
from app.graph.nodes.retrieve_knowledge import retrieve_knowledge
from app.graph.nodes.retrieve_memory import retrieve_memory
from app.graph.nodes.retrieve_profile import retrieve_profile
from app.graph.nodes.retrieve_swing_history import retrieve_swing_history
from app.graph.nodes.rewrite_query import rewrite_query
from app.graph.nodes.save_messages import save_messages
from app.graph.nodes.update_memory import update_memory
from app.graph.nodes.validate_output import validate_output
from app.graph.routing import (
    route_after_evaluate,
    route_after_save_messages,
    route_after_validate,
)
from app.graph.state import CoachState
from app.llm.base import BaseLLMClient


def build_coach_workflow(db: Session, llm: BaseLLMClient):
    graph = StateGraph(CoachState)

    graph.add_node("load_context", partial(load_context, db=db))
    graph.add_node("classify_question", partial(classify_question, llm=llm))
    graph.add_node("retrieve_profile", partial(retrieve_profile, db=db))
    graph.add_node("retrieve_swing_history", partial(retrieve_swing_history, db=db))
    graph.add_node("retrieve_memory", partial(retrieve_memory, db=db))
    graph.add_node("retrieve_knowledge", partial(retrieve_knowledge, db=db))
    graph.add_node("invoke_tools", partial(invoke_tools, db=db))
    graph.add_node("generate_answer", partial(generate_answer, llm=llm))
    graph.add_node("validate_output", validate_output)
    graph.add_node("evaluate_answer", evaluate_answer)
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("fallback_answer", fallback_answer)
    graph.add_node("guardrail", guardrail)
    graph.add_node("save_messages", partial(save_messages, db=db))
    graph.add_node("update_memory", partial(update_memory, db=db, llm=llm))
    graph.add_node("log_eval", partial(log_eval, db=db))

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "classify_question")
    graph.add_edge("classify_question", "retrieve_profile")
    graph.add_edge("retrieve_profile", "retrieve_swing_history")
    graph.add_edge("retrieve_swing_history", "retrieve_memory")
    graph.add_edge("retrieve_memory", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "invoke_tools")
    graph.add_edge("invoke_tools", "generate_answer")
    graph.add_edge("generate_answer", "validate_output")
    graph.add_conditional_edges(
        "validate_output",
        route_after_validate,
        {"evaluate_answer": "evaluate_answer", "guardrail": "guardrail"},
    )
    graph.add_conditional_edges(
        "evaluate_answer",
        route_after_evaluate,
        {
            "guardrail": "guardrail",
            "rewrite_query": "rewrite_query",
            "fallback_answer": "fallback_answer",
        },
    )
    graph.add_edge("rewrite_query", "retrieve_knowledge")
    graph.add_edge("fallback_answer", "save_messages")
    graph.add_edge("guardrail", "save_messages")
    graph.add_conditional_edges(
        "save_messages",
        route_after_save_messages,
        {"update_memory": "update_memory", "log_eval": "log_eval"},
    )
    graph.add_edge("update_memory", "log_eval")
    graph.add_edge("log_eval", END)

    return graph.compile()


def run_coach_workflow(
    db: Session,
    llm: BaseLLMClient,
    *,
    user_id: int,
    conversation_id: int,
    user_message: str,
    trace_id: str,
    latency_ms: int = 0,
) -> CoachState:
    settings = get_settings()
    workflow = build_coach_workflow(db, llm)
    initial: CoachState = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "user_message": user_message,
        "trace_id": trace_id,
        "latency_ms": latency_ms,
        "prompt_version": settings.active_prompt_version,
        "trace": {"trace_id": trace_id},
        "retrieved_chunk_count": 0,
        "retry_count": 0,
        "llm_provider": llm.provider_name,
        "llm_model": llm.model_name,
    }
    invoke_config = build_coach_workflow_invoke_config(
        settings,
        user_id=user_id,
        conversation_id=conversation_id,
        llm_model=llm.model_name,
    )
    invoke_config["recursion_limit"] = max(
        50,
        20 + (settings.quality_max_retries * 8),
    )
    return workflow.invoke(initial, config=invoke_config)
