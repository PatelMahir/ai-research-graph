# API Reference

Base URL (local): `http://localhost:8000`. Interactive docs at `/docs` (Swagger) and
`/redoc`.

## Health

| Method | Path          | Description                          |
|--------|---------------|--------------------------------------|
| GET    | `/api/health` | Liveness — always `{"status":"ok"}`  |
| GET    | `/api/ready`  | Readiness — verifies Redis           |

## Documents

### `POST /api/documents`
Ingest and index a document.

```json
{
  "title": "Attention Is All You Need",
  "text": "The dominant sequence transduction models...",
  "source_uri": "https://arxiv.org/abs/1706.03762",
  "metadata": { "year": 2017 }
}
```

Response `201`:
```json
{
  "id": "…uuid…",
  "title": "Attention Is All You Need",
  "status": "indexed",
  "chunk_count": 12,
  "created_at": "2026-07-10T12:00:00Z"
}
```

### `GET /api/documents`
List ingested documents, newest first.

## Query (RAG)

### `POST /api/query`
```json
{ "question": "What is multi-head attention?", "top_k": 5 }
```

Response `200`:
```json
{
  "answer": "Multi-head attention runs several attention …[0]",
  "sources": [
    { "document_id": "…", "ordinal": 0, "score": 0.83, "excerpt": "…" }
  ]
}
```

## Graph

### `GET /api/graph?limit=200`
Returns nodes and edges of the knowledge graph.

```json
{
  "nodes": [{ "id": "…", "node_type": "paper", "name": "…", "properties": {} }],
  "edges": [{ "source_id": "…", "target_id": "…", "relation": "authored_by", "weight": 2.0 }]
}
```
