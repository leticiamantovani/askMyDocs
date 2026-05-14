import os

from dotenv import load_dotenv
from langchain_postgres import PGVector
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    mailtrap_api_key: str = os.getenv("MAILTRAP_API_KEY", "")
    reset_token_expire_minutes: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


settings = Settings()


def get_vector_store(embeddings, collection_name):
    sync_url = (
        os.getenv("DATABASE_URL", "")
        .replace("postgresql+asyncpg://", "postgresql://", 1)
        .replace("ssl=require", "sslmode=require")
    )
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=sync_url,
    )