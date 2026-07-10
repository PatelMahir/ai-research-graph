"""Relational schema for the research graph.

Nodes (papers, authors, concepts) live in `graph_nodes`; typed edges between them
live in `graph_edges`. Ingested documents and their chunk metadata are tracked so
we can trace every vector back to its source (provenance for retrieval).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NodeType(str, enum.Enum):
    paper = "paper"
    author = "author"
    concept = "concept"
    method = "method"
    dataset = "dataset"
    task = "task"


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(512))
    source_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.pending, index=True
    )
    doc_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    chunk_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), index=True)
    name: Mapped[str] = mapped_column(String(512), index=True)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    out_edges: Mapped[list[GraphEdge]] = relationship(
        back_populates="source", foreign_keys="GraphEdge.source_id"
    )

    __table_args__ = (Index("ix_node_type_name", "node_type", "name", unique=True),)


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("graph_nodes.id", ondelete="CASCADE"), index=True
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("graph_nodes.id", ondelete="CASCADE"), index=True
    )
    relation: Mapped[str] = mapped_column(String(128), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)

    source: Mapped[GraphNode] = relationship(back_populates="out_edges", foreign_keys=[source_id])

    __table_args__ = (
        Index("ix_edge_unique", "source_id", "target_id", "relation", unique=True),
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    ordinal: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(Text)
    vector_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
