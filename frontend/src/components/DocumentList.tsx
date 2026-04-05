import { useEffect, useState } from "react";
import { listDocuments, deleteDocument } from "../api/client";
import type { DocumentMetadata } from "../types";

interface Props {
  refreshKey: number;
}

export default function DocumentList({ refreshKey }: Props) {
  const [docs, setDocs] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchDocs = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await listDocuments();
      setDocs(res.documents);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [refreshKey]);

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      fetchDocs();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete document.");
    }
  };

  if (loading) return <p>Loading documents...</p>;
  if (error) return <p className="error-text">{error}</p>;
  if (docs.length === 0) return <p className="no-docs">No documents uploaded yet.</p>;

  return (
    <div className="document-list">
      <h2>Documents ({docs.length})</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Chunks</th>
            <th>Uploaded</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {docs.map((doc) => (
            <tr key={doc.document_id}>
              <td>{doc.document_name}</td>
              <td>{doc.document_type.toUpperCase()}</td>
              <td>{doc.chunk_count}</td>
              <td>{new Date(doc.upload_date).toLocaleDateString()}</td>
              <td>
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(doc.document_id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
