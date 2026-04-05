export interface DocumentMetadata {
  document_id: string;
  document_name: string;
  document_type: string;
  upload_date: string;
  chunk_count: number;
}

export interface DocumentUploadResponse {
  document_id: string;
  document_name: string;
  chunk_count: number;
  message: string;
}

export interface DocumentListResponse {
  documents: DocumentMetadata[];
  total: number;
}

export interface SourceReference {
  document_name: string;
  chunk_index: number;
  text_excerpt: string;
  similarity_score: number;
}

export interface ConfidenceAssessment {
  score: number;
  level: string;
  reasoning: string;
}

export interface QueryRequest {
  question: string;
  document_filter?: string[];
  top_k?: number;
  conversation_history?: { role: string; content: string }[];
}

export interface QueryResponse {
  answer: string;
  sources: SourceReference[];
  confidence: ConfidenceAssessment;
  disclaimer: string;
}

export interface StatusResponse {
  status: string;
  message: string;
}
