from pydantic import BaseModel, Field
from datetime import datetime


class DocumentMetadata(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    upload_date: str
    chunk_count: int = 0


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    text: str
    chunk_index: int
    metadata: dict = Field(default_factory=dict)


class DocumentUploadResponse(BaseModel):
    document_id: str
    document_name: str
    chunk_count: int
    message: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadata]
    total: int
