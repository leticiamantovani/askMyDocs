from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


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


def get_document_repository(db: AsyncSession = Depends(get_db)):
    from app.repository.document_repository import DocumentRepository
    return DocumentRepository(db)


def get_conversation_service(
    db: AsyncSession = Depends(get_db),
    conversation_repo=Depends(get_conversation_repository),
    message_repo=Depends(get_message_repository),
):
    from app.services.conversation_service import ConversationService
    return ConversationService(db, conversation_repo, message_repo)


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
    from app.services.auth_service import decode_token
    return decode_token(credentials.credentials)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    from app.services.auth_service import decode_token
    return decode_token(credentials.credentials).id
