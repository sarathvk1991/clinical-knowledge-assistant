"""Unit tests for evaluation_service.evaluate_answer().

ChatOpenAI is mocked — no real LLM calls are made.
"""
import json
import pytest
from services.evaluation_service import evaluate_answer

SAMPLE_CHUNKS = [
    {
        "text": "Aspirin inhibits platelet aggregation.",
        "document_name": "pharma.pdf",
        "chunk_index": 1,
        "similarity_score": 0.88,
    }
]
SAMPLE_QUERY = "What does aspirin do?"
SAMPLE_ANSWER = "Aspirin inhibits platelet aggregation."


def _mock_llm(mocker, response_content: str):
    """Patch ChatOpenAI to return a fixed string response."""
    mock_cls = mocker.patch("services.evaluation_service.ChatOpenAI")
    mock_cls.return_value.invoke.return_value.content = response_content
    return mock_cls


# ---------------------------------------------------------------------------
# Test 1: Valid JSON response → parsed correctly
# ---------------------------------------------------------------------------

def test_valid_json_response_is_parsed(mocker):
    _mock_llm(mocker, json.dumps({
        "grounded": True,
        "hallucination": False,
        "score": 0.85,
        "reasoning": "All claims supported by chunks.",
    }))

    result = evaluate_answer(SAMPLE_QUERY, SAMPLE_ANSWER, SAMPLE_CHUNKS)

    assert result["grounded"] is True
    assert result["hallucination"] is False
    assert result["score"] == pytest.approx(0.85)
    assert "prompt_version" in result


# ---------------------------------------------------------------------------
# Test 2: Score > 1 is normalized (divided by 10)
# ---------------------------------------------------------------------------

def test_score_greater_than_one_is_scaled(mocker):
    _mock_llm(mocker, json.dumps({
        "grounded": True,
        "hallucination": False,
        "score": 8.0,
        "reasoning": "Good.",
    }))

    result = evaluate_answer(SAMPLE_QUERY, SAMPLE_ANSWER, SAMPLE_CHUNKS)

    assert result["score"] == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# Test 3: Malformed JSON → fallback triggered
# ---------------------------------------------------------------------------

def test_malformed_json_triggers_fallback(mocker):
    _mock_llm(mocker, "this is not valid json {{{")

    result = evaluate_answer(SAMPLE_QUERY, SAMPLE_ANSWER, SAMPLE_CHUNKS)

    assert result["hallucination"] is True
    assert result["score"] == 0.0


# ---------------------------------------------------------------------------
# Test 4: LLM raises exception → fallback triggered
# ---------------------------------------------------------------------------

def test_llm_exception_triggers_fallback(mocker):
    mock_cls = mocker.patch("services.evaluation_service.ChatOpenAI")
    mock_cls.return_value.invoke.side_effect = Exception("Connection timeout")

    result = evaluate_answer(SAMPLE_QUERY, SAMPLE_ANSWER, SAMPLE_CHUNKS)

    assert result["hallucination"] is True
    assert result["score"] == 0.0


# ---------------------------------------------------------------------------
# Test 5: Empty chunks → fallback (LLM never called)
# ---------------------------------------------------------------------------

def test_empty_chunks_triggers_fallback_without_llm_call(mocker):
    mock_cls = mocker.patch("services.evaluation_service.ChatOpenAI")

    result = evaluate_answer(SAMPLE_QUERY, SAMPLE_ANSWER, chunks=[])

    mock_cls.assert_not_called()
    assert result["hallucination"] is True
    assert "skipped" in result["reasoning"]
