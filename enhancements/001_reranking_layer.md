# Enhancement: Add Reranking Layer to RAG Pipeline

## Context
You are working on an existing FastAPI-based RAG system with the following architecture:

- Retrieval: Pinecone similarity search
- Generation: LLM-based answer generation
- Services are modular (query_service, embedding_service, etc.)
- Async-first design

Current flow:
retrieve → generate

---

## Goal
Introduce a reranking step between retrieval and generation to improve answer relevance.

New flow:
retrieve → rerank → generate

---

## Requirements

### 1. New Service
Create `reranker_service.py`

Method:
rerank(query: str, chunks: List[Chunk]) -> List[Chunk]

---

### 2. Input
- user query
- list of retrieved chunks (text + similarity score)

---

### 3. Output
- re-ranked chunks (most relevant first)
- return top N chunks (default: 3–5)

---

## Reranking Logic (Phase 1 - LLM-based)

- Use existing LLM service to score each chunk
- For each chunk:
  - Evaluate relevance to query
  - Prefer factual correctness over semantic similarity

### Prompt Behavior
- Assign a relevance score (0–1 or 1–10)
- Return structured output (JSON preferred)

---

## Integration Changes

Update `query_service`:

Old:
retrieve → generate

New:
1. Retrieve top 10 chunks
2. Call reranker
3. Select top 3–5 chunks
4. Pass reranked chunks to LLM

---

## Logging

Log the following:
- Retrieved chunks (before reranking)
- Reranked order
- Scores assigned

---

## Configuration

- Add config: `RERANK_ENABLED`
- Add config: `RERANK_TOP_K`

---

## Constraints

- Do NOT rewrite existing services
- Keep changes minimal and modular
- Maintain async compatibility
- Avoid tight coupling with retrieval service
- Keep latency impact low

---

## Output Expectations

- New file: `reranker_service.py`
- Updated `query_service.py`
- Example LLM prompt used for scoring
- Any config changes

Only show modified or new files.
Do not regenerate the entire project.