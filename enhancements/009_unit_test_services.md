Act as a senior Python backend engineer.

Generate unit tests for a production-grade GenAI backend.

---

## Context

The system contains the following services:

1. confidence_service.compute_confidence(chunks: list[dict]) -> dict
2. evaluation_service.evaluate_answer(query, answer, chunks) -> dict
3. reranker_service.rerank(query, chunks, top_k) -> (list[dict], dict[int, float])

---

## Requirements

### General
- Use pytest
- Use pytest-mock for mocking
- Do NOT call external services (LLM, Pinecone)
- Keep tests deterministic

---

## 1. Confidence Service Tests

Create: tests/unit/test_confidence_service.py

Test cases:

1. High similarity + low variance → high confidence
2. Low similarity → low confidence
3. High variance reduces confidence
4. Agreement score impact
5. Empty chunks → score 0, level low

---

## 2. Evaluation Service Tests

Create: tests/unit/test_evaluation_service.py

Mock ChatOpenAI.

Test cases:

1. Valid JSON response → parsed correctly
2. Score normalization (>1 → scaled)
3. Malformed JSON → fallback triggered
4. Exception → fallback triggered
5. Empty chunks → fallback

---

## 3. Reranker Service Tests

Create: tests/unit/test_reranker_service.py

Mock ChatOpenAI.

Test cases:

1. Valid JSON ranking → correct ordering
2. Missing indices handled safely
3. Malformed JSON → fallback to original order
4. Empty chunks → returns empty
5. Score normalization (0–1)

---

## Output

Generate:
- 3 complete test files
- proper imports
- working pytest code