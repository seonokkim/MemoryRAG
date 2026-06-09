"""Optional LangSmith / LangChain tracing via environment variables (no SDK import required)."""

from __future__ import annotations

import logging
import os
from typing import Any

from app.core.config import Settings

logger = logging.getLogger(__name__)

_TRACING_ENV_KEYS = (
    "LANGSMITH_TRACING",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "LANGSMITH_ENDPOINT",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_API_KEY",
    "LANGCHAIN_PROJECT",
)


def _effective_api_key(settings: Settings) -> str | None:
    key = (settings.langsmith_api_key or "").strip()
    return key or None


def configure_langsmith(settings: Settings) -> None:
    """
    Configure process env for LangSmith tracing.
    Never raises; local startup must succeed without LangSmith.
    """
    if not settings.langsmith_tracing:
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        for name in (
            "LANGSMITH_API_KEY",
            "LANGCHAIN_API_KEY",
            "LANGCHAIN_ENDPOINT",
        ):
            os.environ.pop(name, None)
        logger.debug("LangSmith tracing disabled (LANGSMITH_TRACING=false)")
        return

    api_key = _effective_api_key(settings)
    if not api_key:
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.warning(
            "LANGSMITH_TRACING=true but LANGSMITH_API_KEY is missing; "
            "LangSmith tracing disabled (app continues normally)"
        )
        return

    endpoint = settings.langsmith_endpoint.rstrip("/")
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = endpoint
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
    os.environ["LANGCHAIN_ENDPOINT"] = endpoint
    logger.info(
        "LangSmith tracing enabled: project=%s endpoint=%s",
        settings.langsmith_project,
        endpoint,
    )


def build_coach_workflow_invoke_config(
    settings: Settings,
    *,
    user_id: int,
    conversation_id: int,
    question_type: str | None = None,
    llm_model: str | None = None,
) -> dict[str, Any]:
    """LangGraph invoke config: thread id, run name, and metadata for optional LangSmith."""
    metadata: dict[str, Any] = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "llm_provider": settings.llm_provider,
        "llm_model": llm_model or "",
        "vector_store_provider": settings.vector_store_provider,
        "prompt_version": settings.active_prompt_version,
        "langsmith_tracing": settings.langsmith_tracing,
    }
    if question_type:
        metadata["question_type"] = question_type

    return {
        "configurable": {"thread_id": str(conversation_id)},
        "run_name": "memory-rag-coach-workflow",
        "metadata": metadata,
    }
