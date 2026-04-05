"""Unit tests for reranker_service.rerank().

ChatOpenAI is mocked — no real LLM calls are made.
Scores from LLM are on a 0–10 scale; service normalizes them to 0–1.
"""
import json
import pytest
from services.reranker_service import rerank


def _chunk(chunk_index: int, text: str = "sample text") -> dict:
    return {
        "text": text,
        "document_name": "doc.pdf",
        "document_id": "doc-1",
        "chunk_index": chunk_index,
        "similarity_score": 0.80,
    }


def _mock_llm(mocker, response_content: str):
    mock_cls = mocker.patch("services.reranker_service.ChatOpenAI")
    mock_cls.return_value.invoke.return_value.content = response_content
    return mock_cls


# ---------------------------------------------------------------------------
# Test 1: Valid JSON ranking → chunks returned in correct order
# ---------------------------------------------------------------------------

def test_valid_ranking_returns_correct_order(mocker):
    chunks = [_chunk(0), _chunk(1), _chunk(2)]
    # LLM scores chunk 1 highest, then 0, then 2
    _mock_llm(mocker, json.dumps([
        {"index": 0, "score": 5.0},
        {"index": 1, "score": 8.0},
        {"index": 2, "score": 3.0},
    ]))

    reranked, score_map = rerank("query", chunks, top_k=3)

    assert reranked[0]["chunk_index"] == 1   # highest score
    assert reranked[1]["chunk_index"] == 0
    assert reranked[2]["chunk_index"] == 2   # lowest score
    assert len(score_map) == 3


# ---------------------------------------------------------------------------
# Test 2: Missing indices in LLM response → handled safely
# ---------------------------------------------------------------------------

def test_missing_indices_handled_safely(mocker):
    chunks = [_chunk(0), _chunk(1), _chunk(2)]
    # LLM only scores chunk 1; chunks 0 and 2 get implicit score 0.0
    _mock_llm(mocker, json.dumps([
        {"index": 1, "score": 9.0},
    ]))

    reranked, score_map = rerank("query", chunks, top_k=3)

    # Chunk 1 must come first; indices 0 and 2 follow with default 0.0
    assert reranked[0]["chunk_index"] == 1
    assert len(reranked) == 3


# ---------------------------------------------------------------------------
# Test 3: Malformed JSON → fallback to original order
# ---------------------------------------------------------------------------

def test_malformed_json_falls_back_to_original_order(mocker):
    chunks = [_chunk(0), _chunk(1), _chunk(2)]
    _mock_llm(mocker, "not valid json {{[")

    reranked, score_map = rerank("query", chunks, top_k=3)

    assert [c["chunk_index"] for c in reranked] == [0, 1, 2]
    assert score_map == {}


# ---------------------------------------------------------------------------
# Test 4: Empty chunks → returns empty immediately (LLM never called)
# ---------------------------------------------------------------------------

def test_empty_chunks_returns_empty_without_llm_call(mocker):
    mock_cls = mocker.patch("services.reranker_service.ChatOpenAI")

    reranked, score_map = rerank("query", [], top_k=3)

    mock_cls.assert_not_called()
    assert reranked == []
    assert score_map == {}


# ---------------------------------------------------------------------------
# Test 5: Scores normalized to [0, 1] range
# ---------------------------------------------------------------------------

def test_scores_are_normalized_to_zero_one(mocker):
    chunks = [_chunk(0), _chunk(1), _chunk(2)]
    _mock_llm(mocker, json.dumps([
        {"index": 0, "score": 0.0},   # → 0.0
        {"index": 1, "score": 5.0},   # → 0.5
        {"index": 2, "score": 10.0},  # → 1.0
    ]))

    _, score_map = rerank("query", chunks, top_k=3)

    assert score_map[0] == pytest.approx(0.0)
    assert score_map[1] == pytest.approx(0.5)
    assert score_map[2] == pytest.approx(1.0)
    assert all(0.0 <= v <= 1.0 for v in score_map.values())
