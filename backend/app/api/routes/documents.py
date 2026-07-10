"""Document ingestion endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentStatus
from app.db.session import get_session
from app.rag.pipeline import ingest_document
from app.schemas.dto import DocumentOut, IngestRequest

router = APIRouter()


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def ingest(payload: IngestRequest, session: AsyncSession = Depends(get_session)):
    document = Document(
        title=payload.title,
        source_uri=payload.source_uri,
        doc_metadata=payload.metadata,
    )
    session.add(document)
    await session.flush()

    try:
        await ingest_document(session, document, payload.text)
    except Exception as exc:  # noqa: BLE001 — mark failed, surface a clean error
        document.status = DocumentStatus.failed
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ingestion failed while embedding or indexing the document.",
        ) from exc

    await session.commit()
    await session.refresh(document)
    return document


@router.get("", response_model=list[DocumentOut])
async def list_documents(session: AsyncSession = Depends(get_session)):
    rows = await session.execute(select(Document).order_by(Document.created_at.desc()))
    return list(rows.scalars().all())
