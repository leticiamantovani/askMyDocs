from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConversationNotFoundError
from app.db.models import Conversation, Message
from app.repository.conversation_repository import ConversationRepository
from app.repository.message_repository import MessageRepository


class ConversationService:
    def __init__(
        self,
        db: AsyncSession,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
    ):
        self.db = db
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def get(self, conversation_id: UUID) -> Conversation:
        conversation = await self.conversation_repo.get(conversation_id)
        if not conversation:
            raise ConversationNotFoundError(f"Conversation not found: {conversation_id}")
        return conversation

    async def create(self, user_id: UUID, title: str | None = None) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self.conversation_repo.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def resolve(self, user_id: UUID, conversation_id: UUID | None) -> Conversation:
        if conversation_id:
            return await self.get(conversation_id)
        conversation = Conversation(user_id=user_id)
        self.conversation_repo.add(conversation)
        await self.db.flush()
        return conversation

    async def list_by_user(self, user_id: UUID) -> list[Conversation]:
        return await self.conversation_repo.list_by_user(user_id)

    async def update_title(self, conversation: Conversation, title: str) -> None:
        conversation.title = title
        await self.db.commit()

    async def list_messages(self, conversation_id: UUID) -> list[Message]:
        await self.get(conversation_id)
        return await self.message_repo.list_by_conversation(conversation_id)

    async def delete(self, conversation_id: UUID, user_id: UUID) -> None:
        conversation = await self.conversation_repo.get(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise ConversationNotFoundError(f"Conversation not found: {conversation_id}")
        await self.conversation_repo.delete(conversation)
