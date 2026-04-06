"""Integration tests for process_query().

All external dependencies (retrieval, reranking, LLM, evaluation, confidence)
are mocked — no real LLM or database calls are made.
"""
import pytest
from types import SimpleNamespace

import services.query_service as qs
from services.query_service import process_query
from core.errors import LLMError

# ---------------------------------------------------------------------------
# Shared fixtures / constants
# ---------------------------------------------------------------------------

SAMPLE_CHUNK = {
    "text": "Aspirin is used as an antiplatelet agent at 81 mg daily for cardiac prophylaxis.",
    "document_name": "pharma_guide.pdf",
    "document_id": "doc-1",
    "chunk_index": 3,
    "similarity_score": 0.92,
}

HIGH_CONFIDENCE = {"score": 0.85, "level": "high", "reasoning": "Well supported by multiple chunks."}
LOW_CONFIDENCE = {"score": 0.30, "level": "low", "reasoning": "Weak or partial support."}
CLEAN_EVAL = {"grounded": True, "hallucination": False, "score": 0.9, "reasoning": "All claims supported."}
HALLUCINATION_EVAL = {"grounded": False, "hallucination": True, "score": 0.1, "reasoning": "Contains unsupported claims."}
LLM_ANSWER = {"answer": "Aspirin is used as an antiplatelet agent.", "sources_used": [], "confidence_note": ""}


@pytest.fixture
def mock_pipeline(mocker):
    """Patch all external dependencies with sane happy-path defaults."""
    settings_mock = mocker.patch.object(qs, "settings")
    settings_mock.rerank_enabled = True
    settings_mock.rerank_top_k = 5
    settings_mock.retrieval_top_k = 5

    mocks = SimpleNamespace(
        retrieve=mocker.patch("services.query_service.retrieve_chunks", return_value=[SAMPLE_CHUNK]),
        rerank=mocker.patch("services.query_service.rerank", return_value=([SAMPLE_CHUNK], {})),
        confidence=mocker.patch("services.query_service.compute_confidence", return_value=HIGH_CONFIDENCE),
        generate=mocker.patch("services.query_service.generate_answer", return_value=LLM_ANSWER),
        evaluate=mocker.patch("services.query_service.evaluate_answer", return_value=CLEAN_EVAL),
    )
    return mocks


# ---------------------------------------------------------------------------
# Test 1: No chunks retrieved → fallback response
# ---------------------------------------------------------------------------

def test_no_chunks_returns_fallback(mock_pipeline):
    mock_pipeline.retrieve.return_value = []

    result = process_query("What is the treatment for sepsis?")

    assert "don't have enough information" in result.answer
    assert result.sources == []
    assert result.confidence.score == 0.0
    assert result.confidence.level == "low"
    mock_pipeline.generate.assert_not_called()
    mock_pipeline.evaluate.assert_not_called()


# ---------------------------------------------------------------------------
# Test 2: Happy path — valid answer, no hallucination, high confidence
# ---------------------------------------------------------------------------

def test_happy_path_returns_full_response(mock_pipeline):
    result = process_query("What is aspirin used for?")

    assert result.answer == LLM_ANSWER["answer"]
    assert len(result.sources) == 1
    assert result.confidence.score == HIGH_CONFIDENCE["score"]
    assert result.evaluation is not None
    assert result.evaluation.hallucination is False
    assert result.evaluation.grounded is True
    assert result.disclaimer


# ---------------------------------------------------------------------------
# Test 3: LLM failure → fallback response
# ---------------------------------------------------------------------------

def test_llm_failure_returns_fallback(mock_pipeline):
    mock_pipeline.generate.side_effect = LLMError("OpenAI timeout")

    result = process_query("What is aspirin used for?")

    assert "don't have enough information" in result.answer
    assert result.sources == []
    assert result.confidence.score == 0.0
    mock_pipeline.evaluate.assert_not_called()


# ---------------------------------------------------------------------------
# Test 4: Hallucination detected → fallback response (answer suppressed)
# ---------------------------------------------------------------------------

def test_hallucination_detected_returns_fallback(mock_pipeline):
    mock_pipeline.evaluate.return_value = HALLUCINATION_EVAL

    result = process_query("What is aspirin used for?")

    assert "I am not fully confident in this answer." in result.answer
    assert result.confidence.score > 0.0
    # Original LLM answer must NOT appear
    # assert LLM_ANSWER["answer"] not in result.answer


# ---------------------------------------------------------------------------
# Test 5: Low confidence → answer prefixed with caution warning
# ---------------------------------------------------------------------------

def test_low_confidence_prefixes_warning(mock_pipeline):
    mock_pipeline.confidence.return_value = LOW_CONFIDENCE

    result = process_query("What is aspirin used for?")

    assert "\u26a0\ufe0f" in result.answer  # ⚠️
    assert "not fully confident" in result.answer
    assert LLM_ANSWER["answer"] in result.answer  # original answer still present
    assert len(result.sources) == 1


# ---------------------------------------------------------------------------
# Test 6: Empty LLM answer → fallback response
# ---------------------------------------------------------------------------

def test_empty_llm_answer_returns_fallback(mock_pipeline):
    mock_pipeline.generate.return_value = {"answer": "", "sources_used": []}

    result = process_query("What is aspirin used for?")

    assert "don't have enough information" in result.answer
    assert result.sources == []
    assert result.confidence.score == 0.0
    mock_pipeline.evaluate.assert_not_called()
