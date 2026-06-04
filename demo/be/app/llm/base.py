from abc import ABC, abstractmethod
from typing import Any

from app.schemas.coach import StructuredCoachingOutput


class BaseLLMClient(ABC):
    """LLM provider contract. LangGraph nodes call sync helpers; HTTP/async callers use async methods."""

    @abstractmethod
    def classify_question_sync(self, message: str, context: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def generate_structured_answer_sync(
        self,
        message: str,
        question_type: str,
        context: dict[str, Any],
    ) -> StructuredCoachingOutput:
        ...

    @abstractmethod
    def extract_memory_sync(
        self, message: str, answer: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        ...

    async def classify_question(self, message: str, context: dict[str, Any]) -> str:
        return self.classify_question_sync(message, context)

    async def generate_structured_answer(
        self,
        message: str,
        question_type: str,
        context: dict[str, Any],
    ) -> StructuredCoachingOutput:
        return self.generate_structured_answer_sync(message, question_type, context)

    async def extract_memory(
        self, message: str, answer: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        return self.extract_memory_sync(message, answer, context)
