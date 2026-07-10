"""RAG query endpoint."""

from fastapi import APIRouter

from app.rag.pipeline import answer_question
from app.schemas.dto import QueryRequest, QueryResponse

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query(payload: QueryRequest) -> QueryResponse:
    return await answer_question(payload.question, payload.top_k)
