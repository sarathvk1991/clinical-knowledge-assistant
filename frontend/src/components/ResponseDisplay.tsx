import { useState } from "react";
import type { DebugChunk, QueryResponse } from "../types";

interface Props {
  response: QueryResponse | null;
  loading: boolean;
}

interface CollapsibleProps {
  title: string;
  children: React.ReactNode;
}

function Collapsible({ title, children }: CollapsibleProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="debug-collapsible">
      <button
        type="button"
        className="debug-collapsible-header"
        onClick={() => setOpen((o) => !o)}
      >
        <span>{open ? "▾" : "▸"}</span> {title}
      </button>
      {open && <div className="debug-collapsible-body">{children}</div>}
    </div>
  );
}

function DebugChunkList({ chunks }: { chunks: DebugChunk[] }) {
  return (
    <div className="debug-chunk-list">
      {chunks.map((c, i) => (
        <div key={i} className="debug-chunk-item">
          <div className="debug-chunk-header">
            <strong>{c.document_name}</strong>
            <span>Chunk {c.chunk_index}</span>
            {c.similarity_score !== undefined && (
              <span>Similarity: {(c.similarity_score * 100).toFixed(1)}%</span>
            )}
            {c.rerank_score !== undefined && (
              <span>Rerank: {(c.rerank_score * 100).toFixed(1)}%</span>
            )}
          </div>
          <p className="debug-chunk-text">{c.text_excerpt}</p>
        </div>
      ))}
    </div>
  );
}

function confidenceBadge(level: string) {
  const colors: Record<string, string> = {
    high: "#16a34a",
    moderate: "#ca8a04",
    low: "#dc2626",
    no_evidence: "#6b7280",
  };
  return (
    <span
      className="confidence-badge"
      style={{ backgroundColor: colors[level] || "#6b7280" }}
    >
      {level.toUpperCase()}
    </span>
  );
}

export default function ResponseDisplay({ response, loading }: Props) {
  if (loading) {
    return (
      <div className="response-section">
        <div className="loading-indicator">Analyzing clinical documents...</div>
      </div>
    );
  }

  if (!response) return null;

  return (
    <div className="response-section">
      <div className="answer-card">
        <div className="answer-header">
          <h3>Answer</h3>
          {confidenceBadge(response.confidence.level)}
        </div>
        <p className="answer-text">{response.answer}</p>

        <div className="confidence-detail">
          <strong>Confidence:</strong> {(response.confidence.score * 100).toFixed(1)}%
          &mdash; {response.confidence.reasoning}
        </div>

        {response.sources.length > 0 && (
          <div className="sources">
            <h4>Sources</h4>
            {response.sources.map((src, i) => (
              <div key={i} className="source-card">
                <div className="source-header">
                  <strong>{src.document_name}</strong>
                  <span>Chunk {src.chunk_index}</span>
                  <span className="sim-score">
                    Similarity: {(src.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="source-excerpt">{src.text_excerpt}</p>
              </div>
            ))}
          </div>
        )}

        <div className="disclaimer">{response.disclaimer}</div>
      </div>

      {response.debug && (
        <div className="debug-section">
          <h4 className="debug-section-title">Debug Info</h4>
          {response.debug.retrieved_chunks && response.debug.retrieved_chunks.length > 0 && (
            <Collapsible title={`Retrieved Chunks (${response.debug.retrieved_chunks.length})`}>
              <DebugChunkList chunks={response.debug.retrieved_chunks} />
            </Collapsible>
          )}
          {response.debug.reranked_chunks && response.debug.reranked_chunks.length > 0 && (
            <Collapsible title={`Reranked Chunks (${response.debug.reranked_chunks.length})`}>
              <DebugChunkList chunks={response.debug.reranked_chunks} />
            </Collapsible>
          )}
          {response.debug.final_selected_chunks && response.debug.final_selected_chunks.length > 0 && (
            <Collapsible title={`Final Selected Chunks (${response.debug.final_selected_chunks.length})`}>
              <DebugChunkList chunks={response.debug.final_selected_chunks} />
            </Collapsible>
          )}
        </div>
      )}
    </div>
  );
}
