import importlib
import sys
from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.llm.gemini_api_client import GeminiAPIClient, GeminiConfigurationError
from app.llm.factory import get_llm_client
from app.schemas.coach import StructuredCoachingOutput


class TestGeminiAPIClient:
    def test_requires_api_key(self) -> None:
        with pytest.raises(GeminiConfigurationError, match="GEMINI_API_KEY"):
            GeminiAPIClient(Settings(llm_provider="gemini_api", gemini_api_key=""))

    def test_factory_selects_gemini_client(self) -> None:
        for name in ("app.llm.gemini_api_client", "app.llm"):
            sys.modules.pop(name, None)
        importlib.invalidate_caches()
        client = get_llm_client(
            Settings(
                llm_provider="gemini_api",
                gemini_api_key="test-key",
                gemini_model="gemini-2.5-flash",
            )
        )
        assert client.__class__.__name__ == "GeminiAPIClient"

    def test_classify_question_sync(self) -> None:
        client = GeminiAPIClient(
            Settings(llm_provider="gemini_api", gemini_api_key="test-key")
        )
        with patch.object(
            client, "_generate_text", return_value='{"question_type": "swing_diagnosis"}'
        ):
            result = client.classify_question_sync("Why do I keep slicing?", {})
        assert result == "swing_diagnosis"

    def test_generate_structured_answer_sync(self) -> None:
        client = GeminiAPIClient(
            Settings(llm_provider="gemini_api", gemini_api_key="test-key")
        )
        payload = (
            '{"summary":"Test","cause":"Cause","fix":"Fix",'
            '"recommended_drill":"Drill","expected_effect":"Effect",'
            '"sources":["swing_history"],"confidence":0.9}'
        )
        with patch.object(client, "_generate_text", return_value=payload):
            result = client.generate_structured_answer_sync(
                "Why slice?", "swing_diagnosis", {"user_profile": {}}
            )
        assert isinstance(result, StructuredCoachingOutput)
        assert result.summary == "Test"
        assert result.confidence == 0.9

    def test_classify_falls_back_on_bad_json(self) -> None:
        client = GeminiAPIClient(
            Settings(llm_provider="gemini_api", gemini_api_key="test-key")
        )
        with patch.object(client, "_generate_text", return_value="not json"):
            result = client.classify_question_sync("Why do I keep slicing?", {})
        assert result == "swing_diagnosis"
