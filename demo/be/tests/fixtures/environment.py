import os

import pytest

from app.core.config import get_settings
from app.core.database import reset_engine


def _apply_test_env() -> None:
    """Force isolated test env — never inherit live `.env` LLM/LangSmith settings."""
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["VECTOR_STORE_PROVIDER"] = "none"
    os.environ["ENABLE_MEMORY_UPDATE"] = "true"
    os.environ["ENABLE_GUARDRAIL"] = "true"
    os.environ["ENABLE_QUALITY_LOOP"] = "true"
    os.environ["ENABLE_AGENT_TOOLS"] = "true"
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ.pop("LANGSMITH_API_KEY", None)
    os.environ.pop("LANGCHAIN_API_KEY", None)


_apply_test_env()


@pytest.fixture(scope="session", autouse=True)
def _configure_test_env() -> None:
    get_settings.cache_clear()
    reset_engine()
