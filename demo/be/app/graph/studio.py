"""LangGraph Studio entrypoint — visualizes the real 16-node coach workflow.

Import path (langgraph.json):
  ./app/graph/studio.py:graph

Run from demo/be:
  langgraph dev --config langgraph.json --studio-url https://apac.smith.langchain.com

MySQL must be running with seed data (user_id=1) for retrieval nodes.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.observability import configure_langsmith
from app.graph.workflow import build_coach_workflow
from app.llm.factory import get_llm_client

# All nodes in build_coach_workflow() — Studio should show these, not model/tools.
COACH_GRAPH_NODES: tuple[str, ...] = (
    "load_context",
    "classify_question",
    "retrieve_profile",
    "retrieve_swing_history",
    "retrieve_memory",
    "retrieve_knowledge",
    "invoke_tools",
    "generate_answer",
    "validate_output",
    "evaluate_answer",
    "rewrite_query",
    "fallback_answer",
    "guardrail",
    "save_messages",
    "update_memory",
    "log_eval",
)

_settings = get_settings()
configure_langsmith(_settings)

_db = SessionLocal()
_llm = get_llm_client(_settings)

# Exported for LangGraph Studio — same compiled graph as FastAPI run_coach_workflow().
graph = build_coach_workflow(db=_db, llm=_llm)

# Initial state for Studio manual invoke (matches CoachState in app/graph/state.py).
STUDIO_SAMPLE_INPUT: dict = {
    "user_id": 1,
    "conversation_id": 1,
    "user_message": "Why do I keep slicing my driver?",
    "messages": [],
    "trace_id": "studio-dev",
    "latency_ms": 0,
    "prompt_version": _settings.active_prompt_version,
    "trace": {"trace_id": "studio-dev"},
    "retrieved_chunk_count": 0,
    "retry_count": 0,
    "llm_provider": _llm.provider_name,
    "llm_model": _llm.model_name,
}
