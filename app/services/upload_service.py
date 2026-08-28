import logging
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import DomainError, PayloadTooLargeError, ValidationError
from app.db.models.documents import Document
from app.ingestion.indexer import index_chunks
from app.ingestion.loader import iter_pdf_pages, stream_size, validate_pdf_header
from app.ingestion.splitter import iter_chunks
from app.repository.document_repository import DocumentRepository
from app.schema.documents import DocumentResponse

logger = logging.getLogger(__name__)


async def upload_pdf_service(
    user_id: UUID,
    file: UploadFile,
    db: AsyncSession,
) -> DocumentResponse:
    logger.info("upload start user=%s file=%s", user_id, file.filename)

    # Starlette spooled the body already: in memory while small, on disk past
    # ~1MB. Reading it into bytes would undo that, so the stream is passed
    # straight through to pypdf and consumed one page at a time.
    stream = file.file

    size = stream_size(stream)
    if size == 0:
        raise ValidationError("Uploaded file is empty.")
    if size > settings.max_pdf_bytes:
        limit_mb = settings.max_pdf_bytes // (1024 * 1024)
        logger.warning("upload rejected size=%d user=%s", size, user_id)
        raise PayloadTooLargeError(f"PDF is larger than the {limit_mb}MB limit.")
    validate_pdf_header(stream)

    doc_id = uuid4()
    collection_name = f"user_{user_id}_{doc_id}"

    try:
        indexed = await index_chunks(iter_chunks(iter_pdf_pages(stream)), collection_name)
    except DomainError:
        await _drop_collection(db, collection_name)
        raise
    except Exception:
        logger.exception("failed to parse PDF user=%s file=%s", user_id, file.filename)
        await _drop_collection(db, collection_name)
        raise ValidationError(
            "Could not read the PDF file. Make sure it is a valid, non-corrupted PDF."
        )

    if indexed == 0:
        await _drop_collection(db, collection_name)
        raise ValidationError(
            "No text could be extracted from this PDF. Scanned or image-only "
            "PDFs are not supported."
        )

    logger.info("indexed %d chunks user=%s file=%s", indexed, user_id, file.filename)

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


async def _drop_collection(db: AsyncSession, collection_name: str) -> None:
    """Discard a half-written collection so a failed upload leaves no orphan.

    Best effort: a cleanup failure must not mask the error that caused it.
    """
    try:
        await DocumentRepository(db).delete_embeddings(collection_name)
    except Exception:
        logger.exception("failed to clean up collection %s", collection_name)
