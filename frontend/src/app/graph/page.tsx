import { GraphView } from "@/components/GraphView";
import { api } from "@/lib/api";

// Server component — fetch the graph on the server, then render client-side SVG.
export default async function GraphPage() {
  let content;
  try {
    const graph = await api.graph();
    content = <GraphView nodes={graph.nodes} edges={graph.edges} />;
  } catch {
    content = (
      <p className="muted">
        Could not reach the API. Is the backend running on{" "}
        {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}?
      </p>
    );
  }

  return (
    <section className="panel">
      <h2>Knowledge graph</h2>
      <p className="muted">
        Nodes are papers, authors, concepts, methods, datasets, and tasks. Edge thickness
        reflects relation weight (how often the relation was reinforced during ingestion).
      </p>
      {content}
    </section>
  );
}

export const dynamic = "force-dynamic";
