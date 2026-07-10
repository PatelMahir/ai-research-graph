# Architecture

## Overview

AI Research Graph turns unstructured AI papers into a queryable knowledge graph plus a
semantic retrieval layer. Two complementary stores back it:

- **PostgreSQL** — the source of truth for graph nodes/edges, documents, and chunk
  provenance.
- **Qdrant** (vector DB) — embeddings for semantic retrieval. Pluggable via
  `VECTOR_BACKEND` (Pinecone / Weaviate adapters slot into the same `VectorStore`
  protocol).

## Backend layering (transport → service → data)

```
app/
├── api/routes/     transport — FastAPI routers, request validation
├── rag/            service   — pipeline, embeddings, vector store
├── graph/          service   — knowledge-graph construction
├── db/             data      — SQLAlchemy models + async session
├── schemas/        DTOs      — Pydantic request/response contracts
└── core/           cross-cutting — logging, redis
```

## Ingestion flow

1. `POST /api/documents` accepts title + text.
2. `rag.pipeline.ingest_document` splits text (LangChain `RecursiveCharacterTextSplitter`),
   embeds each chunk, and upserts vectors to Qdrant.
3. Chunk rows (with `vector_id`) are persisted for provenance, so every retrieved vector
   traces back to a source document.
4. `graph.builder` upserts paper/author/concept nodes and typed edges idempotently
   (re-ingesting strengthens edge weights rather than duplicating).

## Query flow

1. `POST /api/query` embeds the question and retrieves top-k chunks from Qdrant.
2. The chunks form grounded context for the LLM (`ChatOpenAI`), which must cite sources
   by ordinal.
3. Response returns the answer plus the source chunks and scores.

## RAG: LangChain + LlamaIndex

- **LangChain** drives the online path: text splitting and (optionally) the chat model call.
- **LlamaIndex** (`llama-index-vector-stores-qdrant`) is available for richer index
  construction (node parsers, graph/summary indices) as ingestion grows more structured.

### No-API-key default

The stack runs fully offline out of the box:

- **Embeddings** — `LocalHashingEmbeddings` (deterministic signed feature hashing, L2
  normalized). No model download, no network. Config: `EMBEDDING_PROVIDER=local`.
- **Answers** — extractive: the top retrieved passages are returned with citations, no
  LLM call. Config: `LLM_PROVIDER=none`.

Set `EMBEDDING_PROVIDER=openai` / `LLM_PROVIDER=openai` (with `OPENAI_API_KEY`) to switch
to OpenAI embeddings and grounded synthesis. Those imports are lazy, so the default path
never loads the OpenAI client.

## Redis

Caching (query results, embeddings) and a lightweight job queue for async re-indexing.

## Data model

See `backend/app/db/models.py`:
- `documents`, `chunks` — ingestion + provenance
- `graph_nodes`, `graph_edges` — the research graph (typed nodes, weighted edges)

## Migrations

`alembic.ini` is included. Table auto-create on boot is for local dev only — use Alembic
migrations in staging/production.
