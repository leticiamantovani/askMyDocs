from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.documents import Document
from app.ingestion.indexer import index_chunks
from app.ingestion.loader import extract_text_from_pdf
from app.ingestion.splitter import split_text
from app.repository.document_repository import DocumentRepository
from app.schema.documents import DocumentResponse


async def upload_pdf_service(
    user_id: UUID,
    file: UploadFile,
    db: AsyncSession,
) -> DocumentResponse:
    content = await file.read()
    text = extract_text_from_pdf(content)

    doc_id = uuid4()
    collection_name = f"user_{user_id}_{doc_id}"

    chunks = split_text(text)
    await index_chunks(chunks, collection_name)

    document = Document(
        id=doc_id,
        user_id=user_id,
        filename=file.filename or "untitled.pdf",
        collection_name=collection_name,
    )
    repo = DocumentRepository(db)
    repo.add(document)
    await db.commit()

    return DocumentResponse.model_validate(document)
