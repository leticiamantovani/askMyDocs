import logging
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.documents import Document
from app.ingestion.indexer import index_chunks
from app.ingestion.loader import extract_text_from_pdf
from app.ingestion.splitter import split_text
from app.repository.document_repository import DocumentRepository
from app.core.exceptions import ValidationError
from app.schema.documents import DocumentResponse

logger = logging.getLogger(__name__)


async def upload_pdf_service(
    user_id: UUID,
    file: UploadFile,
    db: AsyncSession,
) -> DocumentResponse:
    logger.info("upload start user=%s file=%s", user_id, file.filename)
    content = await file.read()
    try:
        text = extract_text_from_pdf(content)
    except Exception:
        logger.exception("failed to parse PDF user=%s file=%s", user_id, file.filename)
        raise ValidationError("Could not read the PDF file. Make sure it is a valid, non-corrupted PDF.")

    doc_id = uuid4()
    collection_name = f"user_{user_id}_{doc_id}"

    chunks = split_text(text)
    logger.info("indexing %d chunks user=%s file=%s", len(chunks), user_id, file.filename)
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
