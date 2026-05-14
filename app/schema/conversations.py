from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: UUID
    content: str
    role: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: UUID
    title: str | None
    created_at: datetime
    messages: list[MessageResponse] = []
    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    id: UUID
    title: str | None
    document_id: UUID | None = None
    created_at: datetime
    model_config = {"from_attributes": True}