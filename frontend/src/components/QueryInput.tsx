import { useState, type FormEvent } from "react";
import { submitQuery } from "../api/client";
import type { QueryResponse } from "../types";

interface Props {
  onResponse: (response: QueryResponse) => void;
  onLoading: (loading: boolean) => void;
}

export default function QueryInput({ onResponse, onLoading }: Props) {
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
  const [debugMode, setDebugMode] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setError("");
    onLoading(true);
    try {
      const res = await submitQuery({ question: question.trim(), debug: debugMode || undefined });
      onResponse(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="query-section">
      <h2>Ask a Clinical Question</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your clinical question..."
          rows={3}
        />
        <div className="debug-toggle">
          <label>
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => setDebugMode(e.target.checked)}
            />
            {" "}Show Debug Info
          </label>
        </div>
        <button type="submit" className="btn-primary" disabled={!question.trim()}>
          Submit Query
        </button>
      </form>
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
