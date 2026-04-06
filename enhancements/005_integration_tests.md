Act as a senior Python backend engineer.

Generate integration tests for a production-grade FastAPI-based RAG system.

---

## Context

The system has a core function:

process_query(
    question: str,
    document_filter: list[str] | None = None,
    top_k: int | None = None,
    conversation_history: list[dict] | None = None,
    debug: bool = False,
) -> QueryResponse

---

## Architecture

The pipeline includes:

- retrieve_chunks()
- rerank()
- compute_confidence()
- generate_answer()
- evaluate_answer()

Failure handling includes:
- No chunks → fallback response
- LLM failure → fallback response
- Empty answer → fallback response
- Hallucination → fallback response
- Low confidence → warning prefix added

---

## Goal

Create integration tests for process_query()

---

## Requirements

### 1. Use pytest

### 2. Mock ALL external dependencies:
- retrieval_service.retrieve_chunks
- reranker_service.rerank
- llm_service.generate_answer
- evaluation_service.evaluate_answer
- confidence_service.compute_confidence

DO NOT call real LLM or DB.

---

## 3. Test Cases (MANDATORY)

### Test 1: No chunks retrieved
- retrieve_chunks returns []
- Expect fallback response
- Assert answer contains "don't have enough information"

---

### Test 2: Happy path
- Valid chunks returned
- Valid LLM answer
- evaluation: no hallucination
- confidence: high

Assertions:
- answer returned
- sources present
- evaluation present

---

### Test 3: LLM failure
- generate_answer raises exception
- Expect fallback response

---

### Test 4: Hallucination detected
- evaluation returns hallucination=True
- Expect fallback response (answer suppressed)

---

### Test 5: Low confidence
- confidence score < 0.4
- Expect answer prefixed with warning

---

### Test 6: Empty LLM answer
- generate_answer returns {"answer": ""}
- Expect fallback response

---

## 4. Structure

Create file:

tests/integration/test_query_service.py

---

## 5. Use pytest-mock (mocker fixture)

Example:

mocker.patch("services.retrieval_service.retrieve_chunks", return_value=[...])

---

## 6. Keep tests clean and readable

- One scenario per test
- Clear assertions
- Minimal duplication

---

## 7. Output

Generate:
- Full test file
- Proper imports
- Working pytest code