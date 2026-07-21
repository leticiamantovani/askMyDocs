import asyncio

from app.db.vector_store import get_vector_store
from app.llm.client import get_embeddings


async def retrieve_documents(
    question: str, collection_name: str, k: int = 10
) -> list[str]:
    embeddings = get_embeddings()
    question_embedding = await asyncio.to_thread(embeddings.embed_query, question)
    vector_store = get_vector_store(collection_name)
    results = await asyncio.to_thread(
        vector_store.similarity_search_by_vector, question_embedding, k=k
    )
    return [doc.page_content for doc in results]


async def retrieve(question: str, collection_name: str, k: int = 10) -> str:
    documents = await retrieve_documents(question, collection_name, k)
    return "\n\n".join(documents)
