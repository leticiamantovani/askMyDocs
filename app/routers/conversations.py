from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_conversation_service, get_current_user_id
from app.schema.conversations import ConversationListItem, ConversationResponse, MessageResponse
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationListItem])
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.list_by_user(UUID(user_id))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ConversationResponse)
async def create_conversation(
    user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.create(UUID(user_id))


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.get(conversation_id)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.list_messages(conversation_id)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
):
    await service.delete(conversation_id, UUID(user_id))
