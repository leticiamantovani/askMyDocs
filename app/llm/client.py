from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings


@lru_cache(maxsize=1)
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="retrieval_document",
        output_dimensionality=768,
    )


@lru_cache(maxsize=1)
def get_model():
    return init_chat_model("google_genai:gemini-2.5-flash")
