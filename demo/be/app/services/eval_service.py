from app.repositories.conversation_repository import ConversationRepository
from app.repositories.eval_repository import EvalRepository
from app.schemas.dev import ConversationTraceResponse, PromptVersionItem
from sqlalchemy.orm import Session


class EvalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EvalRepository(db)
        self.conversations = ConversationRepository(db)

    def _workflow_trace_for_conversation(self, conversation_id: int) -> dict:
        for message in reversed(self.conversations.list_messages(conversation_id, limit=50)):
            if message.role != "assistant" or not message.retrieved_context_json:
                continue
            trace = message.retrieved_context_json.get("trace")
            if isinstance(trace, dict):
                return trace
        return {}

    def get_conversation_trace(self, conversation_id: int) -> ConversationTraceResponse:
        log = self.repo.latest_for_conversation(conversation_id)
        workflow_trace = self._workflow_trace_for_conversation(conversation_id)
        log_eval_trace = (
            workflow_trace.get("log_eval") if isinstance(workflow_trace, dict) else {}
        )
        if not isinstance(log_eval_trace, dict):
            log_eval_trace = {}

        def _meta(key: str):
            if isinstance(workflow_trace, dict) and workflow_trace.get(key) is not None:
                return workflow_trace.get(key)
            return log_eval_trace.get(key)

        if not log:
            return ConversationTraceResponse(
                conversation_id=conversation_id,
                workflow="coach_chat",
                prompt_version="v0.3",
                latency_ms=None,
                retrieved_chunk_count=0,
                guardrail_status=None,
                failure_type=None,
                retrieved_sources=[],
                llm_provider=_meta("llm_provider"),
                llm_model=_meta("llm_model"),
                quality_status=_meta("quality_status"),
                retry_count=_meta("retry_count"),
                trace=workflow_trace,
            )
        trace = {**workflow_trace, "eval_log_id": log.id}
        return ConversationTraceResponse(
            conversation_id=conversation_id,
            workflow=log.workflow_name or "coach_chat",
            prompt_version=log.prompt_version or "v0.3",
            latency_ms=log.latency_ms,
            retrieved_chunk_count=log.retrieved_chunk_count or 0,
            guardrail_status=log.guardrail_status,
            failure_type=log.failure_type,
            retrieved_sources=["swing_history", "user_profile", "golf_knowledge"],
            llm_provider=_meta("llm_provider"),
            llm_model=_meta("llm_model"),
            quality_status=_meta("quality_status"),
            retry_count=_meta("retry_count"),
            trace=trace,
        )

    def list_prompt_versions(self) -> list[PromptVersionItem]:
        versions = self.repo.list_prompt_versions()
        return [
            PromptVersionItem(
                name=v.name,
                version=v.version,
                is_active=v.is_active,
                created_at=v.created_at.isoformat(),
            )
            for v in versions
        ]
