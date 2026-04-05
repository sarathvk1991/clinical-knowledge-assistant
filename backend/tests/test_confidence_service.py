from services.confidence_service import compute_confidence


def test_no_chunks_returns_no_evidence():
    result = compute_confidence([])
    assert result["score"] == 0.0
    assert result["level"] == "no_evidence"


def test_high_confidence_with_good_scores():
    chunks = [
        {"similarity_score": 0.95},
        {"similarity_score": 0.92},
        {"similarity_score": 0.90},
        {"similarity_score": 0.88},
        {"similarity_score": 0.91},
    ]
    result = compute_confidence(chunks)
    assert result["level"] == "high"
    assert result["score"] >= 0.7


def test_low_confidence_with_poor_scores():
    chunks = [{"similarity_score": 0.2}]
    result = compute_confidence(chunks)
    assert result["level"] in ["low", "medium"]
    assert result["score"] < 0.7


def test_moderate_confidence():
    chunks = [
        {"similarity_score": 0.7},
        {"similarity_score": 0.65},
        {"similarity_score": 0.6},
    ]
    result = compute_confidence(chunks)
    assert result["level"] in ("medium", "high")
    assert 0.0 <= result["score"] <= 1.0


def test_score_bounded_between_0_and_1():
    chunks = [{"similarity_score": 1.0}] * 10
    result = compute_confidence(chunks)
    assert 0.0 <= result["score"] <= 1.0

    chunks = [{"similarity_score": 0.0}]
    result = compute_confidence(chunks)
    assert 0.0 <= result["score"] <= 1.0
