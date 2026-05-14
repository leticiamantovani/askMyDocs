import asyncio
import io
from uuid import UUID, uuid4

from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_vector_store
from app.core.dependencies import create_chunks, create_embeddings
from app.db.models.documents import Document
from app.repository.document_repository import DocumentRepository
from app.schema.documents import DocumentResponse


async def upload_pdf_service(
    user_id: UUID,
    file: UploadFile,
    db: AsyncSession,
) -> DocumentResponse:
    content = await file.read()

    reader = PdfReader(io.BytesIO(content))
    text = "\n".join(page.extract_text() for page in reader.pages)

    doc_id = uuid4()
    collection_name = f"user_{user_id}_{doc_id}"

    embeddings = create_embeddings()
    chunks = create_chunks(text)

    vector_store = get_vector_store(embeddings, collection_name)
    await asyncio.to_thread(vector_store.create_collection)
    await asyncio.to_thread(vector_store.add_documents, chunks)

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
