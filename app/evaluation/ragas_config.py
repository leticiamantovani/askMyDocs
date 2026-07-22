"""RAGAS judge configuration.

RAGAS uses an LLM + embeddings as the "judge" to score each metric.
We reuse the project's Gemini stack so evaluation runs with the same
provider as production (no OpenAI key required).
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper

from app.llm.client import get_embeddings

# Model used as the RAGAS judge. Kept separate from the app's answering
# model so the two can be tuned independently.
JUDGE_MODEL = "gemini-2.5-flash"


def get_ragas_llm() -> LangchainLLMWrapper:
    # temperature=0 for deterministic, reproducible scoring.
    return LangchainLLMWrapper(
        ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0)
    )


def get_ragas_embeddings() -> LangchainEmbeddingsWrapper:
    return LangchainEmbeddingsWrapper(get_embeddings())
