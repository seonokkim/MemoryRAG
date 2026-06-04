from typing import Any

from app.core.config import Settings
from app.llm.mock_client import MockLLMClient
from app.schemas.coach import StructuredCoachingOutput


class OpenAIClient(MockLLMClient):
    """Optional OpenAI provider; falls back to mock logic until API wiring is configured."""

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.openai_api_key

    async def generate_structured_answer(
        self,
        message: str,
        question_type: str,
        context: dict[str, Any],
    ) -> StructuredCoachingOutput:
        if not self.api_key:
            return await super().generate_structured_answer(message, question_type, context)
        return await super().generate_structured_answer(message, question_type, context)
