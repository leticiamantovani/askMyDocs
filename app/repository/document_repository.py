from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.documents import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def add(self, document: Document) -> None:
        self.db.add(document)

    async def list_by_user(self, user_id: UUID) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, document_id: UUID, user_id: UUID) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()
