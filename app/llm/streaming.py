from collections.abc import AsyncIterator
from uuid import UUID

from app.rag.pipeline import RAGState


async def stream_graph_events(
    graph,
    initial_state: RAGState,
    run_id: UUID,
    user_id: str | None,
) -> AsyncIterator[str]:
    config = {
        "run_id": run_id,
        "run_name": "rag-chat",
        "metadata": {"user_id": user_id},
    }

    async for event in graph.astream_events(initial_state, config, version="v2"):
        if event["event"] == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token:
                yield token
