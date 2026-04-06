Act as a senior backend engineer.

Enhance the existing RAG system by adding a debug mode.

---

## Goal

Allow users to optionally inspect the internal RAG pipeline for debugging and evaluation.

---

## Requirements

1. Add a debug flag to query request:
    debug: boolean (default false)

---

2. When debug=true, include additional fields in response:

debug:
- retrieved_chunks (before reranking)
- reranked_chunks (with scores)
- similarity_scores
- rerank_scores
- final_selected_chunks (passed to LLM)

---

3. Implementation Details

- Update request schema to include debug flag
- Update response schema to optionally include debug field
- Modify query_service:

Flow:
retrieve → (store retrieved_chunks)
→ rerank → (store reranked_chunks + scores)
→ select final chunks
→ generate response

- Collect all intermediate data ONLY if debug=true

---

4. Constraints

- Do NOT impact performance when debug=false
- Keep debug logic clean and optional
- Do not break existing API responses

---

5. Logging

- Continue existing logging
- Debug response is separate from logs

---

Generate:
- updated schemas
- query_service changes
- sample debug response