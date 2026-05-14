from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    document_id: UUID | None = None
