import asyncio

from app.db.vector_store import get_vector_store
from app.llm.client import get_embeddings


async def retrieve(question: str, collection_name: str, k: int = 10) -> str:
    embeddings = get_embeddings()
    question_embedding = await asyncio.to_thread(embeddings.embed_query, question)
    vector_store = get_vector_store(collection_name)
    results = await asyncio.to_thread(
        vector_store.similarity_search_by_vector, question_embedding, k=k
    )
    return "\n\n".join(doc.page_content for doc in results)
