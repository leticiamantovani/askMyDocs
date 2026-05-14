from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_chat_service, get_conversation_service, get_current_user_id, get_db
from app.core.exceptions import NotFoundError
from app.repository.document_repository import DocumentRepository
from app.schema.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_class=StreamingResponse)
async def get_answer(
    request: ChatRequest,
    conversation_id: UUID | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    uid = UUID(user_id)

    if request.document_id:
        doc = await DocumentRepository(db).get_by_id(request.document_id, uid)
        if not doc:
            raise NotFoundError("Document not found")
        collection_name = doc.collection_name
    else:
        collection_name = f"user_{user_id}"

    conversation = await conversation_service.resolve(uid, conversation_id)
    auto_title = request.question[:60].strip() if not conversation.title else None

    stream = await chat_service.stream_answer(
        conversation, request.question, collection_name, auto_title, user_id
    )
    return StreamingResponse(
        stream,
        media_type="text/plain",
        headers={"X-Conversation-ID": str(conversation.id)},
    )
