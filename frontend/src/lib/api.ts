const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface DocumentOut {
  id: string;
  title: string;
  status: string;
  chunk_count: number;
  created_at: string;
}

export interface SourceChunk {
  document_id: string;
  ordinal: number;
  score: number;
  excerpt: string;
}

export interface QueryResponse {
  answer: string;
  sources: SourceChunk[];
}

export interface GraphNode {
  id: string;
  node_type: string;
  name: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  source_id: string;
  target_id: string;
  relation: string;
  weight: number;
}

export interface GraphOut {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listDocuments: () => request<DocumentOut[]>("/api/documents"),
  ingest: (body: { title: string; text: string; source_uri?: string }) =>
    request<DocumentOut>("/api/documents", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  query: (question: string, topK = 5) =>
    request<QueryResponse>("/api/query", {
      method: "POST",
      body: JSON.stringify({ question, top_k: topK }),
    }),
  graph: () => request<GraphOut>("/api/graph"),
};
