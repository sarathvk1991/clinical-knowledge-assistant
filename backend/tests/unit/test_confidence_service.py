"""Unit tests for confidence_service.compute_confidence().

No external dependencies — pure logic only.

Formula:
  score = 0.4*avg_similarity + 0.2*chunk_count_score + 0.2*variance_score + 0.2*agreement_score

Levels: high ≥ 0.75 | medium ≥ 0.4 | low < 0.4
"""
import pytest
from services.confidence_service import compute_confidence


def _chunk(score: float) -> dict:
    return {"similarity_score": score, "text": "x", "document_name": "doc", "chunk_index": 0}


# ---------------------------------------------------------------------------
# Test 1: High similarity + low variance → high confidence
# ---------------------------------------------------------------------------

def test_high_similarity_low_variance_produces_high_confidence():
    # 5 chunks all clustered tightly around 0.90–0.92
    chunks = [_chunk(s) for s in [0.90, 0.91, 0.92, 0.91, 0.90]]
    result = compute_confidence(chunks)

    assert result["score"] >= 0.75
    assert result["level"] == "high"
    assert "avg similarity" in result["reasoning"]


# ---------------------------------------------------------------------------
# Test 2: Low similarity drives score toward low level
# ---------------------------------------------------------------------------

def test_low_similarity_with_high_variance_produces_low_confidence():
    # 1 outlier at 0.99, rest near 0 → avg=0.206, variance_score=0, agreement=0.2
    chunks = [_chunk(s) for s in [0.99, 0.01, 0.01, 0.01, 0.01]]
    result = compute_confidence(chunks)

    assert result["score"] < 0.4
    assert result["level"] == "low"


# ---------------------------------------------------------------------------
# Test 3: High variance reduces confidence vs. low variance (same avg)
# ---------------------------------------------------------------------------

def test_high_variance_reduces_confidence():
    # Low-variance set: all near 0.7, avg ≈ 0.7
    low_var_chunks = [_chunk(s) for s in [0.70, 0.70, 0.70, 0.70, 0.70]]
    # High-variance set: same avg 0.7 but wide spread
    high_var_chunks = [_chunk(s) for s in [0.10, 0.50, 0.70, 0.90, 1.00]]

    low_var_result = compute_confidence(low_var_chunks)
    high_var_result = compute_confidence(high_var_chunks)

    assert low_var_result["score"] > high_var_result["score"]
    assert "variance" in low_var_result["reasoning"]


# ---------------------------------------------------------------------------
# Test 4: Agreement score impact — high agreement scores better than low
# ---------------------------------------------------------------------------

def test_high_agreement_scores_better_than_low_agreement():
    # High agreement: all chunks close to top (0.88), within 0.1
    high_agreement = [_chunk(s) for s in [0.82, 0.84, 0.85, 0.86, 0.88]]
    # Low agreement: only the top chunk is near top, rest far below
    low_agreement = [_chunk(s) for s in [0.88, 0.30, 0.30, 0.30, 0.30]]

    high_result = compute_confidence(high_agreement)
    low_result = compute_confidence(low_agreement)

    assert high_result["score"] > low_result["score"]
    assert "agreement" in high_result["reasoning"]


# ---------------------------------------------------------------------------
# Test 5: Empty chunks → score 0, level no_evidence
# ---------------------------------------------------------------------------

def test_empty_chunks_returns_no_evidence():
    result = compute_confidence([])

    assert result["score"] == 0.0
    assert result["level"] == "no_evidence"
    assert "No relevant chunks" in result["reasoning"]
