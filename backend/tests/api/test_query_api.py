"""API tests for POST /api/query.

process_query is mocked — no real pipeline runs.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from main import app
from models.query import QueryResponse, ConfidenceAssessment, DebugInfo

client = TestClient(app)

QUERY_URL = "/api/query"


def _make_response(**kwargs) -> QueryResponse:
    defaults = {
        "answer": "Aspirin inhibits platelet aggregation.",
        "sources": [],
        "confidence": ConfidenceAssessment(score=0.85, level="high", reasoning="Well supported."),
    }
    defaults.update(kwargs)
    return QueryResponse(**defaults)


# ---------------------------------------------------------------------------
# Test 1: Valid request → 200 with answer
# ---------------------------------------------------------------------------

def test_valid_query_returns_200(mocker):
    mocker.patch("api.query.process_query", return_value=_make_response())

    response = client.post(QUERY_URL, json={"question": "What is aspirin used for?"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "Aspirin inhibits platelet aggregation."
    assert "confidence" in data
    assert "disclaimer" in data


# ---------------------------------------------------------------------------
# Test 2: Missing question field → 422 validation error
# ---------------------------------------------------------------------------

def test_missing_question_returns_422():
    response = client.post(QUERY_URL, json={"document_filter": ["doc-1"]})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test 3: debug=true → debug field present in response
# ---------------------------------------------------------------------------

def test_debug_flag_is_forwarded_and_debug_field_present(mocker):
    mock_process = mocker.patch(
        "api.query.process_query",
        return_value=_make_response(
            debug=DebugInfo(
                retrieved_chunks=[],
                reranked_chunks=[],
                similarity_scores=[],
                rerank_scores=[],
                final_selected_chunks=[],
            )
        ),
    )

    response = client.post(QUERY_URL, json={"question": "What is aspirin?", "debug": True})

    assert response.status_code == 200
    # Verify debug=True was forwarded to process_query
    _, kwargs = mock_process.call_args
    assert kwargs.get("debug") is True
    # Verify debug field is in the response body
    assert "debug" in response.json()


# ---------------------------------------------------------------------------
# Test 4: session_id is accepted and forwarded
# ---------------------------------------------------------------------------

def test_session_id_is_forwarded_to_process_query(mocker):
    mock_process = mocker.patch("api.query.process_query", return_value=_make_response())

    response = client.post(
        QUERY_URL,
        json={"question": "What is aspirin?", "session_id": "session-abc-123"},
    )

    assert response.status_code == 200
    _, kwargs = mock_process.call_args
    assert kwargs.get("session_id") == "session-abc-123"
