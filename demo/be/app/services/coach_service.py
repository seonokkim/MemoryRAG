import asyncio
import time

from app.core.errors import not_found
from app.graph.workflow import run_coach_workflow
from app.llm import get_llm_client
from app.models import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.coach import CoachChatRequest, CoachChatResponse, StructuredCoachingOutput
from app.utils.ids import new_trace_id
from app.utils.time import ms_since
from sqlalchemy.orm import Session


class CoachService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.conversations = ConversationRepository(db)
        self.llm = get_llm_client()

    def _ensure_conversation(self, user_id: int, conversation_id: int | None) -> int:
        if conversation_id:
            conv = self.conversations.get(conversation_id)
            if not conv or conv.user_id != user_id:
                raise not_found("Conversation", conversation_id or 0)
            return conv.id
        conv = self.conversations.create(
            Conversation(user_id=user_id, title="AI Coach", status="active")
        )
        self.db.commit()
        return conv.id

    async def chat(self, request: CoachChatRequest) -> CoachChatResponse:
        if not self.users.get_by_id(request.user_id):
            raise not_found("User", request.user_id)

        trace_id = new_trace_id()
        start = time.perf_counter()
        conversation_id = self._ensure_conversation(request.user_id, request.conversation_id)

        result = await asyncio.to_thread(
            run_coach_workflow,
            self.db,
            self.llm,
            user_id=request.user_id,
            conversation_id=conversation_id,
            user_message=request.message,
            trace_id=trace_id,
            latency_ms=ms_since(start),
        )
        self.db.commit()

        structured_raw = result.get("structured_output")
        structured = None
        if isinstance(structured_raw, StructuredCoachingOutput):
            structured = structured_raw
        elif structured_raw:
            structured = StructuredCoachingOutput.model_validate(structured_raw)

        return CoachChatResponse(
            message_id=result.get("assistant_message_id", 0),
            conversation_id=conversation_id,
            answer=result.get("final_answer", ""),
            structured_output=structured,
            sources=result.get("retrieved_sources", []),
            latency_ms=result.get("latency_ms", ms_since(start)),
            trace_id=trace_id,
            guardrail_status=result.get("guardrail_status", "passed"),
            failure_type=result.get("failure_type"),
        )
