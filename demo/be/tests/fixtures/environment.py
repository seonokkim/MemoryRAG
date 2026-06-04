import os

import pytest

from app.core.config import get_settings
from app.core.database import reset_engine


def _apply_test_env() -> None:
    os.environ.setdefault("LLM_PROVIDER", "mock")
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("VECTOR_STORE_PROVIDER", "none")
    os.environ.setdefault("ENABLE_MEMORY_UPDATE", "true")
    os.environ.setdefault("ENABLE_GUARDRAIL", "true")


_apply_test_env()


@pytest.fixture(scope="session", autouse=True)
def _configure_test_env() -> None:
    get_settings.cache_clear()
    reset_engine()
