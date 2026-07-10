"use client";

import { useState } from "react";
import { api, type QueryResponse } from "@/lib/api";

export function QueryPanel() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onAsk() {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await api.query(question));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <textarea
        rows={3}
        placeholder="e.g. Which methods improve retrieval for long documents?"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={onAsk} disabled={loading || !question.trim()}>
        {loading ? "Thinking…" : "Ask"}
      </button>

      {error && <p className="muted">⚠ {error}</p>}

      {result && (
        <div style={{ marginTop: 16 }}>
          <p className="answer">{result.answer}</p>
          {result.sources.map((s, i) => (
            <div className="source" key={i}>
              [{s.ordinal}] score {s.score.toFixed(3)} — {s.excerpt}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
