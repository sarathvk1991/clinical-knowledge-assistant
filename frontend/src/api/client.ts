import type {
  DocumentListResponse,
  DocumentUploadResponse,
  QueryRequest,
  QueryResponse,
  StatusResponse,
} from "../types";

// In production set VITE_API_BASE_URL to your backend's URL (e.g. https://my-api.onrender.com).
// In Docker dev this is left empty and the Vite proxy handles /api → http://backend:8000.
const BASE_URL = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api`
  : "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function uploadDocument(
  file: File
): Promise<DocumentUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<DocumentUploadResponse>("/documents/upload", {
    method: "POST",
    body: form,
  });
}

export async function listDocuments(): Promise<DocumentListResponse> {
  return request<DocumentListResponse>("/documents");
}

export async function deleteDocument(id: string): Promise<StatusResponse> {
  return request<StatusResponse>(`/documents/${id}`, { method: "DELETE" });
}

export async function submitQuery(req: QueryRequest): Promise<QueryResponse> {
  return request<QueryResponse>("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
}
