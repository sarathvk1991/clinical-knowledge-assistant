Act as a senior backend engineer working on a production-grade clinical RAG system.

Enhance the existing query_service.py by adding robust failure handling logic.

---

## Context

The system already has:
- retrieval (retrieve_chunks)
- reranking (rerank)
- confidence scoring (compute_confidence)
- answer generation (generate_answer)
- evaluation layer (evaluate_answer)

You must integrate failure handling WITHOUT breaking the current structure or response schema.

---

## Requirements

### 1. No Retrieved Chunks

If no chunks are retrieved:

- Skip reranking, LLM, and evaluation
- Return a safe fallback response

Response:
"I don’t have enough information to answer this question based on the available documents."

- confidence.score = 0.0
- confidence.level = "low"
- evaluation.hallucination = true

---

### 2. LLM Failure Handling

Wrap generate_answer() in try/except:

- On failure:
  - Log error
  - Return fallback response
  - Do NOT crash API

---

### 3. Hallucination Handling (Using Evaluation)

After evaluation:

If:
evaluation["hallucination"] == True

Then:
- Log warning
- Return fallback response (do NOT return original answer)

---

### 4. Low Confidence Handling

If:
confidence["score"] < 0.4

Then:
- Do NOT discard answer
- Modify answer to include warning:

"⚠️ Note: I am not fully confident in this answer. Please verify with a healthcare professional."

---

### 5. Helper Functions

Create clean helper functions inside query_service.py:

- _fallback_response(reason: str) -> QueryResponse
- _cautious_response(answer: str) -> str

Keep them simple and reusable.

---

### 6. Constraints

- Do NOT change existing API response schema
- Do NOT remove existing debug functionality
- Do NOT modify chunk objects
- Keep logic clean and readable
- Ensure evaluation failure does NOT break response
- Maintain logging at each failure point

---

### 7. Flow (Final Behavior)

retrieve
  → if no chunks → fallback

rerank
  → generate (try/except)
  → evaluate

  → if hallucination → fallback
  → if low confidence → modify answer

return response

---

## Output

Generate:
- Updated query_service.py with:
  - failure handling logic
  - helper functions
  - proper logging

Ensure code is clean, production-ready, and consistent with existing style.