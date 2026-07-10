"""Knowledge-graph read endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GraphEdge, GraphNode
from app.db.session import get_session
from app.schemas.dto import EdgeOut, GraphOut, NodeOut

router = APIRouter()


@router.get("", response_model=GraphOut)
async def get_graph(
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    node_rows = await session.execute(select(GraphNode).limit(limit))
    nodes = list(node_rows.scalars().all())
    node_ids = {n.id for n in nodes}

    edge_rows = await session.execute(select(GraphEdge))
    edges = [
        EdgeOut(
            source_id=e.source_id,
            target_id=e.target_id,
            relation=e.relation,
            weight=e.weight,
        )
        for e in edge_rows.scalars().all()
        if e.source_id in node_ids and e.target_id in node_ids
    ]

    return GraphOut(nodes=[NodeOut.model_validate(n) for n in nodes], edges=edges)
