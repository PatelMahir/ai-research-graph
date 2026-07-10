"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, graph, health, query
from app.core.logging import configure_logging, get_logger
from app.db.session import engine
from app.db.base import Base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("starting_up")
    # Create tables on boot (use Alembic migrations in production).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("shutting_down")
    await engine.dispose()


app = FastAPI(
    title="AI Research Graph API",
    version="0.1.0",
    description="Ingest AI research, build a knowledge graph, and query it with RAG.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
