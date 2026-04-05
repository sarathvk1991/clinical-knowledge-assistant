import type { QueryResponse } from "../types";

interface Props {
  response: QueryResponse | null;
  loading: boolean;
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
    </div>
  );
}
