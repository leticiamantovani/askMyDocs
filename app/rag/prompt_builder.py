import asyncio

from app.db.models import Message
from app.services.prompt_registry import PromptRegistry


async def build_prompt(
    question: str,
    context: str,
    history: list[Message],
    user_id: str | None,
    user_name: str | None,
) -> str:
    registry = PromptRegistry.get()
    prompt_template = await registry.resolve("rag-prompt", user_id=user_id)

    history_block = "\n".join(f"{m.role}: {m.content}" for m in history)
    user_name_header = f"Hi {user_name},\n\n" if user_name else ""
    return await asyncio.to_thread(
        prompt_template.format,
        context=context,
        history=history_block,
        question=question,
        user_name=user_name_header,
    )
