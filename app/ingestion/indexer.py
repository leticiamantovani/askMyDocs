import asyncio

from langchain_core.documents import Document

from app.db.vector_store import get_vector_store


async def index_chunks(chunks: list[Document], collection_name: str) -> None:
    vector_store = get_vector_store(collection_name)
    await asyncio.to_thread(vector_store.create_collection)
    await asyncio.to_thread(vector_store.add_documents, chunks)
