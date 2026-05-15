import os

from langchain_postgres import PGVector

from app.llm.client import get_embeddings


def get_vector_store(collection_name: str) -> PGVector:
    sync_url = (
        os.getenv("DATABASE_URL", "")
        .replace("postgresql+asyncpg://", "postgresql://", 1)
        .replace("ssl=require", "sslmode=require")
    )
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=collection_name,
        connection=sync_url,
    )
