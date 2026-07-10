"""initial schema: documents, chunks, graph nodes/edges

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

node_type = sa.Enum(
    "paper", "author", "concept", "method", "dataset", "task", name="nodetype"
)
doc_status = sa.Enum(
    "pending", "processing", "indexed", "failed", name="documentstatus"
)


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("source_uri", sa.String(1024), nullable=True),
        sa.Column("status", doc_status, nullable=False, server_default="pending"),
        sa.Column("doc_metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_documents_status", "documents", ["status"])

    op.create_table(
        "graph_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("node_type", node_type, nullable=False),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("properties", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_graph_nodes_node_type", "graph_nodes", ["node_type"])
    op.create_index("ix_graph_nodes_name", "graph_nodes", ["name"])
    op.create_index("ix_node_type_name", "graph_nodes", ["node_type", "name"], unique=True)

    op.create_table(
        "graph_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("graph_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("graph_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("relation", sa.String(128), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("properties", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_graph_edges_source_id", "graph_edges", ["source_id"])
    op.create_index("ix_graph_edges_target_id", "graph_edges", ["target_id"])
    op.create_index("ix_graph_edges_relation", "graph_edges", ["relation"])
    op.create_index(
        "ix_edge_unique", "graph_edges", ["source_id", "target_id", "relation"], unique=True
    )

    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("vector_id", sa.String(128), nullable=True),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])


def downgrade() -> None:
    op.drop_table("chunks")
    op.drop_table("graph_edges")
    op.drop_table("graph_nodes")
    op.drop_table("documents")
    node_type.drop(op.get_bind(), checkfirst=True)
    doc_status.drop(op.get_bind(), checkfirst=True)
