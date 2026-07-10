"""Embedding factory.

Defaults to a **local, no-network hashing embedder** so the platform runs without any
API keys. Set `EMBEDDING_PROVIDER=openai` (and `OPENAI_API_KEY`) to use OpenAI embeddings.
"""

from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache
from typing import Protocol

from app.config import get_settings

_TOKEN = re.compile(r"[a-z0-9]+")


class Embeddings(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


class LocalHashingEmbeddings:
    """Deterministic signed feature-hashing embedder.

    Bag-of-words tokens are hashed into ``dim`` buckets with a sign bit, then the vector
    is L2-normalized. No model download, no network — good enough for local dev, demos,
    and tests. Swap for a real embedding model in production.
    """

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _TOKEN.findall(text.lower()):
            digest = hashlib.md5(token.encode()).digest()
            h = int.from_bytes(digest[:8], "little")
            bucket = h % self.dim
            sign = 1.0 if digest[8] & 1 else -1.0
            vec[bucket] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


@lru_cache
def get_embeddings() -> Embeddings:
    settings = get_settings()
    if settings.embedding_provider == "local":
        return LocalHashingEmbeddings(dim=settings.embedding_dim)
    if settings.embedding_provider == "openai":
        # Imported lazily so the local path never requires the openai/langchain-openai stack.
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
    raise NotImplementedError(
        f"Embedding provider '{settings.embedding_provider}' not wired up yet."
    )
