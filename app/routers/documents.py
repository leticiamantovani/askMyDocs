import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_vector_store
from app.core.dependencies import create_embeddings, get_current_user_id, get_db
from app.core.exceptions import NotFoundError
from app.repository.document_repository import DocumentRepository
from app.schema.documents import DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    return await repo.list_by_user(UUID(user_id))


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    doc = await repo.get_by_id(document_id, UUID(user_id))
    if not doc:
        raise NotFoundError("Document not found")

    embeddings = create_embeddings()
    vector_store = get_vector_store(embeddings, doc.collection_name)
    await asyncio.to_thread(vector_store.delete_collection)

    await repo.delete(doc)
