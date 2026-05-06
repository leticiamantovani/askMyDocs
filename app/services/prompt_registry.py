import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field

from langchain_core.prompts import BasePromptTemplate
from langsmith import Client

logger = logging.getLogger(__name__)

_CACHE_TTL = int(os.getenv("PROMPT_CACHE_TTL_SECONDS", "300"))


@dataclass
class _CacheEntry:
    prompt: BasePromptTemplate
    fetched_at: float = field(default_factory=time.monotonic)

    def is_expired(self) -> bool:
        return time.monotonic() - self.fetched_at > _CACHE_TTL


class PromptRegistry:
    """
    Singleton that resolves prompt versions from LangSmith Hub with in-memory cache.
    In prod with multiple replicas, replace _cache with Redis to share state across instances.
    """

    _instance: "PromptRegistry | None" = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self._cache: dict[str, _CacheEntry] = {}
        self._client = Client()
        self._force_version = os.getenv("PROMPT_FORCE_VERSION")

    @classmethod
    def get(cls) -> "PromptRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def resolve(self, prompt_name: str, user_id: str | None = None) -> BasePromptTemplate:
        """
        Resolves a prompt by version. Priority order:
        1. PROMPT_FORCE_VERSION (emergency override via env var)
        2. feature flag by user_id (A/B experiment)
        3. latest version from Hub
        """
        flag_version = self._resolve_flag(user_id) if user_id else None
        effective_version = self._force_version or flag_version
        cache_key = f"{prompt_name}:{effective_version or 'latest'}"

        async with self._lock:
            entry = self._cache.get(cache_key)
            if entry and not entry.is_expired():
                return entry.prompt

            prompt = await self._fetch(prompt_name, effective_version)
            self._cache[cache_key] = _CacheEntry(prompt=prompt)
            logger.info("Prompt loaded from Hub: %s (version=%s)", prompt_name, effective_version or "latest")
            return prompt

    async def invalidate(self, prompt_name: str, version: str | None = None) -> None:
        """Invalidates cache for a specific version or all entries for the given prompt."""
        keys_to_remove = [
            k for k in self._cache
            if k.startswith(prompt_name) and (version is None or k == f"{prompt_name}:{version}")
        ]
        for k in keys_to_remove:
            del self._cache[k]
        logger.info("Cache invalidated for %s (version=%s)", prompt_name, version or "all")

    @staticmethod
    def _resolve_flag(user_id: str) -> str | None:
        experiment_version = os.getenv("PROMPT_EXPERIMENT_VERSION")
        rollout_pct = int(os.getenv("PROMPT_EXPERIMENT_ROLLOUT", "0"))
        if not experiment_version or rollout_pct == 0:
            return None
        bucket = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
        return experiment_version if bucket < rollout_pct else None

    async def _fetch(self, prompt_name: str, version: str | None) -> BasePromptTemplate:
        ref = f"{prompt_name}:{version}" if version else prompt_name
        return await asyncio.to_thread(self._client.pull_prompt, ref)
