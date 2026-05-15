from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_chat_service, get_conversation_service, get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.repository.document_repository import DocumentRepository
from app.schema.chat import ChatRequest
from app.services.auth_service import TokenData
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_class=StreamingResponse)
async def get_answer(
    request: ChatRequest,
    conversation_id: UUID | None = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    uid = UUID(current_user.id)

    conversation = await conversation_service.resolve(uid, conversation_id)
    auto_title = request.question[:60].strip() if not conversation.title else None

    if request.document_id:
        doc = await DocumentRepository(db).get_by_id(request.document_id, uid)
        if not doc:
            raise NotFoundError("Document not found")
        collection_name = doc.collection_name
        conversation.document_id = request.document_id
    else:
        collection_name = f"user_{current_user.id}"

    stream = await chat_service.stream_answer(
        conversation, request.question, collection_name, auto_title, current_user.id, current_user.name
    )
    return StreamingResponse(
        stream,
        media_type="text/plain",
        headers={"X-Conversation-ID": str(conversation.id)},
    )
