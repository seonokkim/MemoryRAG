import logging
from pathlib import Path
from typing import Any

from app.core.config import Settings
from app.llm.base import BaseLLMClient
from app.llm.json_utils import parse_json_array, parse_json_object
from app.llm.mock_client import MockLLMClient
from app.llm.structured_outputs import QUESTION_TYPES, classify_by_keywords
from app.schemas.coach import StructuredCoachingOutput
from app.utils.json import safe_json_dumps

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


class GeminiConfigurationError(RuntimeError):
    """Raised when LLM_PROVIDER=gemini_api but required settings are missing."""


class GeminiAPIClient(BaseLLMClient):
    """
    Gemini Developer API provider (Google AI Studio API key).
    LangGraph nodes call sync methods. JSON parse failures fall back to mock/keyword logic.
    """

    def __init__(self, settings: Settings) -> None:
        self.api_key = (settings.gemini_api_key or "").strip()
        self._model_id = settings.gemini_model or "gemini-flash-latest"
        if not self.api_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini_api. "
                "Create a key at https://aistudio.google.com/apikey and set it in .env."
            )
        self._client: Any = None
        self._mock_fallback = MockLLMClient()

    @property
    def provider_name(self) -> str:
        return "gemini_api"

    @property
    def model_name(self) -> str:
        return self._model_id

    def _load_prompt(self, filename: str) -> str:
        path = _PROMPTS_DIR / filename
        return path.read_text(encoding="utf-8").strip()

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from google import genai
        except ImportError as exc:
            raise GeminiConfigurationError(
                "google-genai is not installed. Run: pip install google-genai"
            ) from exc
        self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _generate_text(self, prompt: str, *, json_mode: bool = False) -> str:
        try:
            from google.genai import types
        except ImportError as exc:
            raise GeminiConfigurationError(
                "google-genai is not installed. Run: pip install google-genai"
            ) from exc

        client = self._get_client()
        config = None
        if json_mode:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )
        response = client.models.generate_content(
            model=self._model_id,
            contents=prompt,
            config=config,
        )
        text = getattr(response, "text", None) or ""
        text = text.strip()
        if not text:
            raise RuntimeError("Gemini API returned an empty response")
        return text

    def classify_question_sync(self, message: str, context: dict[str, Any]) -> str:
        classifier_prompt = self._load_prompt("question_classifier_prompt.md")
        prompt = (
            f"{classifier_prompt}\n\n"
            f"Allowed types: {', '.join(QUESTION_TYPES)}\n"
            f"User message: {message}\n"
            f"Recent messages (summary): {safe_json_dumps(context.get('messages', [])[:5])}\n\n"
            'Respond with JSON only: {"question_type": "<one allowed type>"}'
        )
        try:
            raw = self._generate_text(prompt, json_mode=True)
            data = parse_json_object(raw)
            if data:
                qtype = str(data.get("question_type", "")).strip()
                if qtype in QUESTION_TYPES:
                    return qtype
        except Exception:
            logger.warning(
                "Gemini classify_question failed; using keyword fallback", exc_info=True
            )
        return classify_by_keywords(message)

    def generate_structured_answer_sync(
        self,
        message: str,
        question_type: str,
        context: dict[str, Any],
    ) -> StructuredCoachingOutput:
        system_prompt = self._load_prompt("coaching_system_prompt.md")
        prompt = (
            f"{system_prompt}\n\n"
            f"Question type: {question_type}\n"
            f"User message: {message}\n"
            f"Context:\n{safe_json_dumps(context)}\n\n"
            "Return JSON only with keys: summary, cause, fix, recommended_drill, "
            "expected_effect, sources (string array), confidence (0.0-1.0)."
        )
        try:
            raw = self._generate_text(prompt, json_mode=True)
            data = parse_json_object(raw)
            if data:
                return StructuredCoachingOutput(
                    summary=str(data.get("summary", "")),
                    cause=str(data.get("cause", "")),
                    fix=str(data.get("fix", "")),
                    recommended_drill=str(data.get("recommended_drill", "")),
                    expected_effect=str(data.get("expected_effect", "")),
                    sources=[str(s) for s in (data.get("sources") or []) if s],
                    confidence=float(data.get("confidence", 0.8)),
                )
        except Exception:
            logger.warning(
                "Gemini generate_structured_answer failed; using mock fallback",
                exc_info=True,
            )
        return self._mock_fallback.generate_structured_answer_sync(
            message, question_type, context
        )

    def extract_memory_sync(
        self, message: str, answer: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        memory_prompt = self._load_prompt("memory_extraction_prompt.md")
        prompt = (
            f"{memory_prompt}\n\n"
            f"User message: {message}\n"
            f"Coach answer: {answer}\n"
            f"Context: {safe_json_dumps(context)}\n\n"
            "Return JSON only: a list of objects with memory_type, content, confidence."
        )
        try:
            raw = self._generate_text(prompt, json_mode=True)
            data = parse_json_array(raw)
            if data is not None:
                items: list[dict[str, Any]] = []
                for row in data:
                    if not isinstance(row, dict) or not row.get("content"):
                        continue
                    items.append(
                        {
                            "memory_type": str(row.get("memory_type", "preference")),
                            "content": str(row["content"]),
                            "confidence": float(row.get("confidence", 0.7)),
                        }
                    )
                return items
        except Exception:
            logger.warning("Gemini extract_memory failed; returning no memories", exc_info=True)
        return []
