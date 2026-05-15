import asyncio
from collections.abc import AsyncIterator
from typing import TypedDict
from uuid import UUID, uuid4

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_vector_store
from app.core.dependencies import create_embeddings, create_model
from app.core.exceptions import NotFoundError
from app.db.models import Conversation, Message
from app.repository.document_repository import DocumentRepository
from app.repository.message_repository import MessageRepository
from app.services.prompt_registry import PromptRegistry

embeddings = create_embeddings()
model = create_model()


class RAGState(TypedDict):
    question: str
    collection_name: str
    conversation_id: UUID
    history: list[Message]
    context: str
    answer: str
    user_id: str | None
    user_name: str | None


async def _retrieve_docs(state: RAGState) -> dict:
    question_embedding = await asyncio.to_thread(embeddings.embed_query, state["question"])
    vector_store = get_vector_store(embeddings, state["collection_name"])
    results = await asyncio.to_thread(
        vector_store.similarity_search_by_vector, question_embedding, k=10
    )

    print("RESSULTS", results)
    return {"context": "\n\n".join(doc.page_content for doc in results)}


async def _generate_answer(state: RAGState) -> dict:
    registry = PromptRegistry.get()
    prompt_template = await registry.resolve(
        "rag-prompt",
        user_id=state.get("user_id"),
    )

    history_block = "\n".join(f"{m.role}: {m.content}" for m in state["history"])
    prompt = await asyncio.to_thread(
        prompt_template.format,
        context=state["context"],
        history=history_block,
        question=state["question"],
        user_name=state.get("user_name") or "",
    )

    response = await model.ainvoke(prompt)
    return {"answer": response.content}


def _build_graph() -> StateGraph:
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", _retrieve_docs)
    graph.add_node("generate", _generate_answer)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


rag_graph = _build_graph()


class ChatService:
    def __init__(self, db: AsyncSession, message_repo: MessageRepository, document_repo: DocumentRepository):
        self.db = db
        self.message_repo = message_repo
        self.document_repo = document_repo

    async def resolve_collection(self, document_id: UUID | None, user_id: UUID) -> str:
        if document_id is None:
            return f"user_{user_id}"
        doc = await self.document_repo.get_by_id(document_id, user_id)
        if not doc:
            raise NotFoundError("Document not found")
        return doc.collection_name

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
        collection_name = await self.resolve_collection(document_id, uid)

        if document_id:
            conversation.document_id = document_id
        history = await self.message_repo.list_by_conversation(conversation.id)

        if auto_title:
            conversation.title = auto_title

        await self.message_repo.save(conversation.id, question, "user")

        run_id = uuid4()
        return self._stream(conversation, question, collection_name, history, run_id, user_id, user_name)

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

        config = {
            "run_id": run_id,
            "run_name": "rag-chat",
            "metadata": {"user_id": user_id},
        }

        buffer: list[str] = []
        try:
            async for event in rag_graph.astream_events(initial_state, config, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    token = event["data"]["chunk"].content
                    if token:
                        buffer.append(token)
                        yield token
        finally:
            if buffer:
                await self.message_repo.save(conversation.id, "".join(buffer), "assistant")
