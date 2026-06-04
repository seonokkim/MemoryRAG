import os

import pytest

from app.core.config import Settings
from app.core.observability import configure_langsmith


class TestLangSmithOptional:
    def test_default_settings_do_not_require_api_key(self) -> None:
        settings = Settings()
        assert settings.langsmith_tracing is False
        assert settings.langsmith_api_key == ""

    def test_tracing_false_does_not_crash(self) -> None:
        configure_langsmith(Settings(langsmith_tracing=False))
        assert os.environ.get("LANGSMITH_TRACING") == "false"
        assert os.environ.get("LANGCHAIN_TRACING_V2") == "false"

    def test_tracing_true_without_api_key_is_non_fatal(self, caplog: pytest.LogCaptureFixture) -> None:
        configure_langsmith(
            Settings(langsmith_tracing=True, langsmith_api_key="")
        )
        assert os.environ.get("LANGSMITH_TRACING") == "false"
        assert "LANGSMITH_API_KEY is missing" in caplog.text

    def test_tracing_true_with_api_key_sets_env(self) -> None:
        configure_langsmith(
            Settings(
                langsmith_tracing=True,
                langsmith_api_key="ls-test-key",
                langsmith_project="MemoryRAG-test",
            )
        )
        assert os.environ.get("LANGSMITH_TRACING") == "true"
        assert os.environ.get("LANGSMITH_API_KEY") == "ls-test-key"
        assert os.environ.get("LANGSMITH_PROJECT") == "MemoryRAG-test"
        assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
        assert os.environ.get("LANGCHAIN_API_KEY") == "ls-test-key"

    def test_app_import_without_langsmith_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "LANGSMITH_TRACING",
            "LANGSMITH_API_KEY",
            "LANGCHAIN_TRACING_V2",
            "LANGCHAIN_API_KEY",
        ):
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("LANGSMITH_TRACING", "false")
        monkeypatch.setenv("LLM_PROVIDER", "mock")
        monkeypatch.setenv("VECTOR_STORE_PROVIDER", "none")

        from app.main import create_app

        assert create_app() is not None

    def test_invoke_config_includes_metadata(self) -> None:
        from app.core.observability import build_coach_workflow_invoke_config

        settings = Settings(llm_provider="mock", vector_store_provider="none")
        cfg = build_coach_workflow_invoke_config(
            settings, user_id=1, conversation_id=2, question_type="swing_diagnosis"
        )
        assert cfg["run_name"] == "MemoryRAG-coach-workflow"
        assert cfg["configurable"]["thread_id"] == "2"
        assert cfg["metadata"]["user_id"] == 1
        assert cfg["metadata"]["question_type"] == "swing_diagnosis"
