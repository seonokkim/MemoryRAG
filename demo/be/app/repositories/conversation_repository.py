from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message


class ConversationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, conversation_id: int) -> Conversation | None:
        return self.db.get(Conversation, conversation_id)

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def list_messages(self, conversation_id: int, limit: int = 20) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def add_message(self, message: Message) -> Message:
        self.db.add(message)
        self.db.flush()
        return message

    def get_message(self, message_id: int) -> Message | None:
        return self.db.get(Message, message_id)
