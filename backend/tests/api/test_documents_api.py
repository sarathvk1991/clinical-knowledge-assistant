"""API tests for document endpoints.

  POST   /api/documents/upload
  GET    /api/documents
  DELETE /api/documents/{document_id}

Service layer is mocked — no real Pinecone or LLM calls.
"""
import pytest
from fastapi.testclient import TestClient

from main import app
from models.document import DocumentUploadResponse, DocumentMetadata
from core.errors import DocumentNotFoundError

client = TestClient(app)

UPLOAD_URL = "/api/documents/upload"
LIST_URL = "/api/documents"


def _doc_meta(doc_id: str = "doc-1") -> DocumentMetadata:
    return DocumentMetadata(
        document_id=doc_id,
        document_name="pharma_guide.txt",
        document_type="txt",
        upload_date="2026-04-05T00:00:00+00:00",
        chunk_count=5,
    )


# ---------------------------------------------------------------------------
# Test 1: Upload document → 200 success response
# ---------------------------------------------------------------------------

def test_upload_document_returns_success(mocker):
    mocker.patch(
        "api.documents.upload_document",
        return_value=DocumentUploadResponse(
            document_id="doc-1",
            document_name="pharma_guide.txt",
            chunk_count=5,
            message="Document 'pharma_guide.txt' uploaded successfully with 5 chunks",
        ),
    )

    response = client.post(
        UPLOAD_URL,
        files={"file": ("pharma_guide.txt", b"Aspirin is an antiplatelet agent.", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc-1"
    assert data["document_name"] == "pharma_guide.txt"
    assert data["chunk_count"] == 5
    assert "message" in data


# ---------------------------------------------------------------------------
# Test 2: List documents → returns list with total
# ---------------------------------------------------------------------------

def test_list_documents_returns_list(mocker):
    mocker.patch(
        "api.documents.list_documents",
        return_value=[_doc_meta("doc-1"), _doc_meta("doc-2")],
    )

    response = client.get(LIST_URL)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["documents"]) == 2
    assert data["documents"][0]["document_id"] == "doc-1"


# ---------------------------------------------------------------------------
# Test 3: Delete document → 200 success
# ---------------------------------------------------------------------------

def test_delete_document_returns_success(mocker):
    mocker.patch("api.documents.delete_document", return_value=None)

    response = client.delete(f"{LIST_URL}/doc-1")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "doc-1" in data["message"]


# ---------------------------------------------------------------------------
# Test 4: Delete non-existent document → 404 error
# ---------------------------------------------------------------------------

def test_delete_nonexistent_document_returns_404(mocker):
    mocker.patch(
        "api.documents.delete_document",
        side_effect=DocumentNotFoundError("doc-missing"),
    )

    response = client.delete(f"{LIST_URL}/doc-missing")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "doc-missing" in data["error"]
