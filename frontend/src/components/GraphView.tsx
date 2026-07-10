"use client";

import { useMemo } from "react";
import type { GraphEdge, GraphNode } from "@/lib/api";

const TYPE_COLORS: Record<string, string> = {
  paper: "#6ea8fe",
  author: "#7ee787",
  concept: "#f0883e",
  method: "#d2a8ff",
  dataset: "#79c0ff",
  task: "#ffa657",
};

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/**
 * Dependency-free force-free layout: nodes are placed on a circle and edges drawn as
 * straight lines. Good enough to visualize small graphs without a heavy graph library.
 */
export function GraphView({ nodes, edges }: Props) {
  const size = 520;
  const radius = size / 2 - 60;
  const center = size / 2;

  const positioned = useMemo(() => {
    return nodes.map((node, i) => {
      const angle = (2 * Math.PI * i) / Math.max(nodes.length, 1);
      return {
        node,
        x: center + radius * Math.cos(angle),
        y: center + radius * Math.sin(angle),
      };
    });
  }, [nodes, center, radius]);

  const byId = useMemo(
    () => new Map(positioned.map((p) => [p.node.id, p])),
    [positioned],
  );

  if (nodes.length === 0) {
    return <p className="muted">No graph yet — ingest a paper to populate nodes.</p>;
  }

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label="Research knowledge graph"
      style={{ width: "100%", maxWidth: size }}
    >
      {edges.map((e, i) => {
        const a = byId.get(e.source_id);
        const b = byId.get(e.target_id);
        if (!a || !b) return null;
        return (
          <line
            key={i}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            stroke="#263149"
            strokeWidth={Math.min(1 + e.weight * 0.5, 4)}
          />
        );
      })}
      {positioned.map(({ node, x, y }) => (
        <g key={node.id}>
          <circle cx={x} cy={y} r={8} fill={TYPE_COLORS[node.node_type] ?? "#93a1bd"} />
          <text x={x + 12} y={y + 4} fill="#e6ebf5" fontSize={11}>
            {node.name.length > 24 ? `${node.name.slice(0, 24)}…` : node.name}
          </text>
        </g>
      ))}
    </svg>
  );
}
