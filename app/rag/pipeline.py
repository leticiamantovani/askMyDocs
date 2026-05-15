from functools import lru_cache
from typing import TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph

from app.db.models import Message
from app.llm.client import get_model
from app.rag.prompt_builder import build_prompt
from app.rag.retriever import retrieve


class RAGState(TypedDict):
    question: str
    collection_name: str
    conversation_id: UUID
    history: list[Message]
    context: str
    answer: str
    user_id: str | None
    user_name: str | None


def build_rag_graph(model) -> StateGraph:
    async def retrieve_node(state: RAGState) -> dict:
        context = await retrieve(state["question"], state["collection_name"])
        return {"context": context}

    async def augment_node(state: RAGState) -> dict:
        prompt = await build_prompt(
            question=state["question"],
            context=state["context"],
            history=state["history"],
            user_id=state.get("user_id"),
            user_name=state.get("user_name"),
        )
        return {"answer": prompt}

    async def generate_node(state: RAGState) -> dict:
        response = await model.ainvoke(state["answer"])
        return {"answer": response.content}

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("augment", augment_node)
    graph.add_node("generate", generate_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "augment")
    graph.add_edge("augment", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


@lru_cache(maxsize=1)
def get_rag_graph():
    return build_rag_graph(get_model())
