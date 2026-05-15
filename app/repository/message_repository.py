from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_conversation(self, conversation_id: UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars())

    async def save(self, conversation_id: UUID, content: str, role: str) -> None:
        self.db.add(Message(conversation_id=conversation_id, content=content, role=role))
        await self.db.commit()
