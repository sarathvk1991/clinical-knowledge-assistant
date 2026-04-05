import { useState } from "react";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";
import QueryInput from "./components/QueryInput";
import ResponseDisplay from "./components/ResponseDisplay";
import StatusBar from "./components/StatusBar";
import type { QueryResponse } from "./types";

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Clinical Knowledge Assistant</h1>
        <p className="subtitle">AI-powered clinical document analysis with source attribution</p>
        <StatusBar />
      </header>

      <main className="app-main">
        <section className="left-panel">
          <DocumentUpload onUploadComplete={() => setRefreshKey((k) => k + 1)} />
          <DocumentList refreshKey={refreshKey} />
        </section>

        <section className="right-panel">
          <QueryInput onResponse={setResponse} onLoading={setLoading} />
          <ResponseDisplay response={response} loading={loading} />
        </section>
      </main>
    </div>
  );
}
