from collections.abc import AsyncIterator
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Message
from app.llm.streaming import stream_graph_events
from app.rag.pipeline import RAGState, get_rag_graph
from app.repository.document_repository import DocumentRepository
from app.repository.message_repository import MessageRepository


class ChatService:
    def __init__(
        self,
        db: AsyncSession,
        message_repo: MessageRepository,
        document_repo: DocumentRepository,
    ):
        self.db = db
        self.message_repo = message_repo
        self.document_repo = document_repo

    async def stream_answer(
        self,
        conversation: Conversation,
        question: str,
        document_id: UUID | None,
        auto_title: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
    ) -> AsyncIterator[str]:
        uid = UUID(user_id) if user_id else None
        collection_name = await self.document_repo.resolve_collection(document_id, uid)

        if document_id:
            conversation.document_id = document_id
        history = await self.message_repo.list_by_conversation(conversation.id)

        if auto_title:
            conversation.title = auto_title

        await self.message_repo.save(conversation.id, question, "user")

        return self._stream(conversation, question, collection_name, history, uuid4(), user_id, user_name)

    async def _stream(
        self,
        conversation: Conversation,
        question: str,
        collection_name: str,
        history: list[Message],
        run_id: UUID,
        user_id: str | None,
        user_name: str | None = None,
    ) -> AsyncIterator[str]:
        initial_state: RAGState = {
            "question": question,
            "collection_name": collection_name,
            "conversation_id": conversation.id,
            "history": history,
            "context": "",
            "answer": "",
            "user_id": user_id,
            "user_name": user_name,
        }

        buffer: list[str] = []
        try:
            async for token in stream_graph_events(get_rag_graph(), initial_state, run_id, user_id):
                buffer.append(token)
                yield token
        finally:
            if buffer:
                await self.message_repo.save(conversation.id, "".join(buffer), "assistant")
