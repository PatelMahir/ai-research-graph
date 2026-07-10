"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function IngestPanel() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onIngest() {
    if (!title.trim() || !text.trim()) return;
    setLoading(true);
    setStatus(null);
    try {
      const doc = await api.ingest({ title, text });
      setStatus(`Indexed "${doc.title}" — ${doc.chunk_count} chunks (${doc.status}).`);
      setTitle("");
      setText("");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <input
        placeholder="Paper title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        rows={5}
        placeholder="Paste abstract or full text…"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={onIngest} disabled={loading || !title.trim() || !text.trim()}>
        {loading ? "Indexing…" : "Ingest"}
      </button>
      {status && <p className="muted">{status}</p>}
    </div>
  );
}
