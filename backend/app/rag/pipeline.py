"""RAG ingest + query pipeline.

Ingestion: split text (LangChain) -> embed -> upsert to the vector store, persisting
chunk provenance in PostgreSQL. Query: embed the question, retrieve top-k chunks, and
compose a grounded answer with the configured LLM.
"""

from __future__ import annotations

import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging import get_logger
from app.db.models import Chunk, Document, DocumentStatus
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import get_vector_store
from app.schemas.dto import QueryResponse, SourceChunk

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are an assistant answering questions about AI research. "
    "Answer only from the provided context. If the context is insufficient, say so. "
    "Cite sources by their [ordinal]."
)


def _splitter() -> RecursiveCharacterTextSplitter:
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


async def ingest_document(session: AsyncSession, document: Document, text: str) -> int:
    """Chunk, embed, and index a document. Returns the number of chunks indexed."""
    document.status = DocumentStatus.processing
    await session.flush()

    pieces = _splitter().split_text(text)
    if not pieces:
        document.status = DocumentStatus.indexed
        return 0

    embeddings = get_embeddings()
    vectors = embeddings.embed_documents(pieces)

    store = get_vector_store()
    store.ensure_collection(dim=len(vectors[0]))

    ids: list[str] = []
    payloads: list[dict] = []
    for ordinal, (content, _vec) in enumerate(zip(pieces, vectors, strict=True)):
        vid = str(uuid.uuid4())
        ids.append(vid)
        payloads.append(
            {
                "document_id": str(document.id),
                "ordinal": ordinal,
                "excerpt": content[:400],
            }
        )
        session.add(
            Chunk(document_id=document.id, ordinal=ordinal, content=content, vector_id=vid)
        )

    store.upsert(ids=ids, vectors=vectors, payloads=payloads)

    document.chunk_count = len(pieces)
    document.status = DocumentStatus.indexed
    logger.info("document_indexed", document_id=str(document.id), chunks=len(pieces))
    return len(pieces)


async def answer_question(question: str, top_k: int) -> QueryResponse:
    """Retrieve relevant chunks and compose a grounded answer."""
    embeddings = get_embeddings()
    query_vec = embeddings.embed_query(question)

    store = get_vector_store()
    hits = store.search(vector=query_vec, top_k=top_k)

    sources = [
        SourceChunk(
            document_id=uuid.UUID(h.payload["document_id"]),
            ordinal=h.payload["ordinal"],
            score=h.score,
            excerpt=h.payload.get("excerpt", ""),
        )
        for h in hits
    ]

    if not sources:
        return QueryResponse(answer="No indexed content matched this question.", sources=[])

    settings = get_settings()
    if settings.llm_provider == "openai" and settings.openai_api_key:
        answer = await _llm_answer(question, sources, settings.llm_model, settings.openai_api_key)
    else:
        answer = _extractive_answer(sources)
    return QueryResponse(answer=answer, sources=sources)


def _extractive_answer(sources: list[SourceChunk]) -> str:
    """No-LLM fallback: surface the most relevant retrieved passages with citations."""
    top = sources[:3]
    body = "\n\n".join(f"[{s.ordinal}] {s.excerpt}" for s in top)
    return (
        "Answer generated without an LLM (set LLM_PROVIDER=openai to enable synthesis). "
        "Most relevant indexed passages:\n\n" + body
    )


async def _llm_answer(question: str, sources: list[SourceChunk], model: str, api_key: str) -> str:
    """Grounded synthesis via OpenAI. Imported lazily so the default path needs no API key."""
    from langchain_openai import ChatOpenAI

    context = "\n\n".join(f"[{s.ordinal}] {s.excerpt}" for s in sources)
    llm = ChatOpenAI(model=model, api_key=api_key, temperature=0)
    completion = await llm.ainvoke(
        [
            ("system", _SYSTEM_PROMPT),
            ("human", f"Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    return completion.content
