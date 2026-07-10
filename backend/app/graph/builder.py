"""Knowledge-graph construction helpers.

Upserts nodes and edges idempotently so re-ingesting a paper strengthens existing
relations (edge weight) rather than duplicating them.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GraphEdge, GraphNode, NodeType


async def upsert_node(
    session: AsyncSession, node_type: NodeType, name: str, properties: dict | None = None
) -> GraphNode:
    stmt = select(GraphNode).where(
        GraphNode.node_type == node_type, GraphNode.name == name
    )
    node = (await session.execute(stmt)).scalar_one_or_none()
    if node is None:
        node = GraphNode(node_type=node_type, name=name, properties=properties or {})
        session.add(node)
        await session.flush()
    return node


async def upsert_edge(
    session: AsyncSession, source: GraphNode, target: GraphNode, relation: str
) -> GraphEdge:
    stmt = select(GraphEdge).where(
        GraphEdge.source_id == source.id,
        GraphEdge.target_id == target.id,
        GraphEdge.relation == relation,
    )
    edge = (await session.execute(stmt)).scalar_one_or_none()
    if edge is None:
        edge = GraphEdge(source_id=source.id, target_id=target.id, relation=relation)
        session.add(edge)
    else:
        edge.weight += 1.0
    await session.flush()
    return edge


async def link_paper_authors(
    session: AsyncSession, paper_title: str, authors: list[str]
) -> GraphNode:
    """Create a paper node and `authored_by` edges to each author."""
    paper = await upsert_node(session, NodeType.paper, paper_title)
    for author_name in authors:
        author = await upsert_node(session, NodeType.author, author_name)
        await upsert_edge(session, paper, author, relation="authored_by")
    return paper
