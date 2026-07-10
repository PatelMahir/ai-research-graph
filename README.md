# AI Research Graph

A platform for building and querying a **knowledge graph of AI research** — ingest papers,
extract entities/relations (authors, methods, datasets, tasks, citations), embed them for
semantic retrieval, and answer questions with a RAG pipeline grounded in the graph.

## Tech Stack

| Layer        | Technology                                  |
|--------------|---------------------------------------------|
| Frontend     | React, Next.js (App Router), TypeScript     |
| Backend      | Python, FastAPI                             |
| RAG          | LangChain, LlamaIndex                       |
| Vector DB    | Qdrant (default) — Pinecone / Weaviate ready |
| Database     | PostgreSQL                                  |
| Cache/Queue  | Redis                                       |
| CI/CD        | GitLab CI                                   |
| Cloud        | AWS (ECS/Fargate, RDS, ElastiCache, S3)     |
| Runtime      | Docker / docker-compose                     |

## Architecture

```
                    ┌─────────────────────┐
                    │  Next.js Frontend   │
                    │  (React + TS)       │
                    └──────────┬──────────┘
                               │ HTTP / JSON
                    ┌──────────▼──────────┐
                    │   FastAPI Backend   │
                    │  transport → service│
                    │        → data       │
                    └───┬────────┬────────┘
        ┌───────────────┤        ├───────────────┐
        │               │        │               │
 ┌──────▼─────┐  ┌──────▼───┐ ┌──▼──────┐  ┌─────▼──────┐
 │ PostgreSQL │  │  Qdrant  │ │  Redis  │  │  RAG core  │
 │ graph +    │  │ vectors  │ │ cache + │  │ LangChain +│
 │ metadata   │  │          │ │ queue   │  │ LlamaIndex │
 └────────────┘  └──────────┘ └─────────┘  └────────────┘
```

## Quick start (local)

```bash
cp .env.example .env
# No API key required — defaults use local hashing embeddings + extractive answers.

docker compose up --build
```

> **No OpenAI key needed by default.** Embeddings run locally (deterministic hashing) and
> answers are extractive (top retrieved passages). To enable OpenAI-backed embeddings and
> LLM synthesis, uncomment `langchain-openai` in `backend/requirements.txt` and set
> `EMBEDDING_PROVIDER=openai`, `LLM_PROVIDER=openai`, and `OPENAI_API_KEY` in `.env`.

Services:
- Frontend → http://localhost:3000
- Backend (FastAPI docs) → http://localhost:8000/docs
- Qdrant dashboard → http://localhost:6333/dashboard
- PostgreSQL → localhost:5432
- Redis → localhost:6379

## Development

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Project layout

```
ai-research-graph/
├── backend/          FastAPI service, RAG pipeline, graph builder
├── frontend/         Next.js app (App Router, TypeScript)
├── infra/            AWS + deployment notes
├── docs/             Architecture & API docs
├── docker-compose.yml
└── .gitlab-ci.yml
```

See [docs/architecture.md](docs/architecture.md) for details.
