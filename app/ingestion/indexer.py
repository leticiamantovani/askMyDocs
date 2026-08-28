import asyncio
from collections.abc import Iterable

from langchain_core.documents import Document

from app.core.config import settings
from app.db.vector_store import get_vector_store


async def index_chunks(chunks: Iterable[Document], collection_name: str) -> int:
    """Embed and store chunks in fixed-size batches, returning how many landed.

    Accepts any iterable so the caller can stream: peak memory is one batch
    rather than every chunk in the document.
    """
    vector_store = get_vector_store(collection_name)
    await asyncio.to_thread(vector_store.create_collection)

    indexed = 0
    batch: list[Document] = []
    for chunk in chunks:
        batch.append(chunk)
        if len(batch) >= settings.index_batch_size:
            await asyncio.to_thread(vector_store.add_documents, batch)
            indexed += len(batch)
            batch = []

    if batch:
        await asyncio.to_thread(vector_store.add_documents, batch)
        indexed += len(batch)

    return indexed
