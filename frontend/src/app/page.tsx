import { QueryPanel } from "@/components/QueryPanel";
import { IngestPanel } from "@/components/IngestPanel";

export default function HomePage() {
  return (
    <>
      <section className="panel">
        <h2>Ask the research graph</h2>
        <p className="muted">
          Questions are answered with retrieval-augmented generation over your indexed
          papers. Every answer is grounded in cited source chunks.
        </p>
        <QueryPanel />
      </section>

      <section className="panel">
        <h2>Ingest a paper</h2>
        <p className="muted">
          Paste text or an abstract. It is chunked, embedded, and indexed into the vector
          store, with provenance tracked in PostgreSQL.
        </p>
        <IngestPanel />
      </section>
    </>
  );
}
