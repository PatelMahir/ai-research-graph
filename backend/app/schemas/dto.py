"""Request/response DTOs. Explicit types on the public API boundary."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    title: str = Field(..., max_length=512)
    text: str = Field(..., min_length=1)
    source_uri: str | None = None
    metadata: dict = Field(default_factory=dict)


class DocumentOut(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    document_id: uuid.UUID
    ordinal: int
    score: float
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class NodeOut(BaseModel):
    id: uuid.UUID
    node_type: str
    name: str
    properties: dict

    model_config = {"from_attributes": True}


class EdgeOut(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation: str
    weight: float


class GraphOut(BaseModel):
    nodes: list[NodeOut]
    edges: list[EdgeOut]
