import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Research Graph",
  description: "Ingest AI research, build a knowledge graph, and query it with RAG.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <span className="brand">AI Research Graph</span>
          <nav className="nav">
            <a href="/">Ask &amp; Ingest</a>
            <a href="/graph">Graph</a>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
