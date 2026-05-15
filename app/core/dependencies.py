from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_vector_store
from app.db.session import AsyncSessionLocal


def create_vector_store(chunks, embeddings, collection_name):
    vector_store = get_vector_store(embeddings, collection_name)
    vector_store.create_collection()
    vector_store.add_documents(chunks)
    return vector_store


def semantic_search(question, embeddings, collection_name):
    question_embedding = embeddings.embed_query(question)
    vector_store = get_vector_store(embeddings, collection_name)
    return vector_store.similarity_search_by_vector(question_embedding, k=2)


def create_chunks(pdf_text: str) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_text(pdf_text)
    return [Document(page_content=t) for t in texts]


def create_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="retrieval_document",
        output_dimensionality=768,
    )


def create_model():
    return init_chat_model("google_genai:gemini-2.5-flash")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_conversation_repository(db: AsyncSession = Depends(get_db)):
    from app.repository.conversation_repository import ConversationRepository
    return ConversationRepository(db)


def get_message_repository(db: AsyncSession = Depends(get_db)):
    from app.repository.message_repository import MessageRepository
    return MessageRepository(db)


def get_conversation_service(
    db: AsyncSession = Depends(get_db),
    conversation_repo=Depends(get_conversation_repository),
    message_repo=Depends(get_message_repository),
):
    from app.services.conversation_service import ConversationService
    return ConversationService(db, conversation_repo, message_repo)


def get_document_repository(db: AsyncSession = Depends(get_db)):
    from app.repository.document_repository import DocumentRepository
    return DocumentRepository(db)


def get_chat_service(
    db: AsyncSession = Depends(get_db),
    message_repo=Depends(get_message_repository),
    document_repo=Depends(get_document_repository),
):
    from app.services.chat_service import ChatService
    return ChatService(db, message_repo, document_repo)


_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    from app.services.auth_service import TokenData, decode_token
    return decode_token(credentials.credentials)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    from app.services.auth_service import decode_token
    return decode_token(credentials.credentials).id
