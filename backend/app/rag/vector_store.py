"""Vector store abstraction.

Qdrant is the default backend. The `VectorStore` protocol keeps the RAG pipeline
independent of the concrete client so Pinecone/Weaviate can be dropped in later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings


@dataclass
class SearchHit:
    vector_id: str
    score: float
    payload: dict


class VectorStore(Protocol):
    def ensure_collection(self, dim: int) -> None: ...
    def upsert(self, ids: list[str], vectors: list[list[float]], payloads: list[dict]) -> None: ...
    def search(self, vector: list[float], top_k: int) -> list[SearchHit]: ...


class QdrantVectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._collection = settings.qdrant_collection
        self._client = QdrantClient(url=settings.qdrant_url)

    def ensure_collection(self, dim: int) -> None:
        existing = {c.name for c in self._client.get_collections().collections}
        if self._collection not in existing:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads) -> None:
        points = [
            qmodels.PointStruct(id=i, vector=v, payload=p)
            for i, v, p in zip(ids, vectors, payloads, strict=True)
        ]
        self._client.upsert(collection_name=self._collection, points=points)

    def search(self, vector, top_k) -> list[SearchHit]:
        results = self._client.search(
            collection_name=self._collection, query_vector=vector, limit=top_k
        )
        return [
            SearchHit(vector_id=str(r.id), score=r.score, payload=r.payload or {}) for r in results
        ]


def get_vector_store() -> VectorStore:
    backend = get_settings().vector_backend
    if backend == "qdrant":
        return QdrantVectorStore()
    raise NotImplementedError(f"Vector backend '{backend}' not wired up yet.")
