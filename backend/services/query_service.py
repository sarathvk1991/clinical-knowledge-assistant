from config import get_settings
from models.query import QueryResponse, SourceReference, ConfidenceAssessment, DebugInfo, DebugChunk
from services.retrieval_service import retrieve_chunks
from services.reranker_service import rerank
from services.confidence_service import compute_confidence
from services.llm_service import generate_answer
from services.evaluation_service import evaluate_answer
from core.logging import logger
from core.errors import LLMError

settings = get_settings()

_RETRIEVAL_FETCH_K = 10
_MAX_HISTORY_MESSAGES = 6  # 3 interactions (1 user + 1 assistant each)

# In-memory session store: session_id -> list of {role, content} dicts
SESSION_STORE: dict[str, list[dict]] = {}

_FALLBACK_ANSWER = (
    "I don't have enough information to answer this question based on the available documents."
)

_CAUTION_PREFIX = (
    "\u26a0\ufe0f Note: I am not fully confident in this answer. "
    "Please verify with a healthcare professional.\n\n"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_minimal_debug(retrieved_chunks, reranked_chunks) -> DebugInfo:
    return DebugInfo(
        retrieved_chunks=[],
        reranked_chunks=[],
        similarity_scores=[],
        rerank_scores=[],
        final_selected_chunks=[],
    )


def _fallback_response(reason: str, debug_info: DebugInfo | None = None) -> QueryResponse:
    logger.warning("Returning fallback response: %s", reason)
    return QueryResponse(
        answer=_FALLBACK_ANSWER,
        sources=[],
        confidence=ConfidenceAssessment(
            score=0.0,
            level="low",
            reasoning=reason,
        ),
        debug=debug_info,
    )


def _cautious_response(answer: str) -> str:
    return _CAUTION_PREFIX + answer


def _get_session_history(session_id: str | None) -> list[dict]:
    if not session_id:
        return []
    return list(SESSION_STORE.get(session_id, []))


def _save_to_session(session_id: str | None, question: str, answer: str) -> None:
    if not session_id:
        return
    history = SESSION_STORE.setdefault(session_id, [])
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    SESSION_STORE[session_id] = history[-_MAX_HISTORY_MESSAGES:]


def _to_debug_chunk(chunk: dict, rerank_score: float | None = None) -> DebugChunk:
    text = chunk["text"]
    return DebugChunk(
        document_name=chunk["document_name"],
        chunk_index=chunk["chunk_index"],
        text_excerpt=text[:200] + "..." if len(text) > 200 else text,
        similarity_score=round(chunk.get("similarity_score", 0.0), 4),
        rerank_score=round(rerank_score, 4) if rerank_score is not None else None,
    )


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

def process_query(
    question: str,
    document_filter: list[str] | None = None,
    top_k: int | None = None,
    conversation_history: list[dict] | None = None,
    debug: bool = False,
    session_id: str | None = None,
) -> QueryResponse:
    logger.info(f"Processing query: {question[:80]}...")

    # Resolve conversation history: session memory takes precedence when session_id is provided
    if session_id:
        conversation_history = _get_session_history(session_id)
        logger.info("Loaded %d messages from session %s", len(conversation_history), session_id)

    # 1. Retrieve
    fetch_k = _RETRIEVAL_FETCH_K if settings.rerank_enabled else (top_k or settings.retrieval_top_k)
    retrieved_chunks = retrieve_chunks(question, top_k=fetch_k, document_filter=document_filter)

    logger.info(
        "Retrieved %d chunks (pre-rerank)",
        len(retrieved_chunks),
        extra={"pre_rerank_chunk_indices": [c.get("chunk_index") for c in retrieved_chunks]},
    )

    if not retrieved_chunks:
        debug_info = _build_minimal_debug([], []) if debug else None
        return _fallback_response("no_chunks", debug_info)

    # 2. Rerank
    score_map: dict[int, float] = {}
    if settings.rerank_enabled:
        reranked_chunks, score_map = rerank(question, retrieved_chunks, top_k=top_k or settings.rerank_top_k)
    else:
        reranked_chunks = retrieved_chunks[: (top_k or settings.retrieval_top_k)]

    final_chunks = reranked_chunks

    # 3. Confidence
    confidence = compute_confidence(final_chunks)

    # 4. Generate
    try:
        llm_result = generate_answer(question, final_chunks, conversation_history)
    except (LLMError, Exception) as e:
        logger.error("LLM generation failed: %s", e)
        debug_info = _build_minimal_debug(retrieved_chunks, reranked_chunks) if debug else None
        return _fallback_response("llm_failure", debug_info)

    answer = llm_result.get("answer", "")
    if not answer:
        debug_info = _build_minimal_debug(retrieved_chunks, reranked_chunks) if debug else None
        return _fallback_response("empty_answer", debug_info)

    # 5. Evaluation
    try:
        evaluation = evaluate_answer(question, answer, final_chunks)
    except Exception as e:
        logger.error("Evaluation failed: %s", e)
        evaluation = {
            "grounded": False,
            "hallucination": True,
            "score": 0.0,
            "reasoning": "evaluation_failed",
        }

    # 🔥 Optional stricter safety (enable if needed)
    # if evaluation["hallucination"] or confidence["score"] < 0.2:
    #     debug_info = _build_minimal_debug(retrieved_chunks, reranked_chunks) if debug else None
    #     return _fallback_response("unsafe_output", debug_info)

    if evaluation.get("hallucination"):
        logger.warning(
            "Hallucination detected",
            extra={"query": question[:100], "evaluation": evaluation},
        )
        debug_info = _build_minimal_debug(retrieved_chunks, reranked_chunks) if debug else None
        return _fallback_response("hallucination_detected", debug_info)

    # 6. Low confidence
    if confidence["score"] < 0.4:
        answer = _cautious_response(answer)

    # 7. Sources
    sources = [
        SourceReference(
            document_name=chunk["document_name"],
            chunk_index=chunk["chunk_index"],
            text_excerpt=chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            similarity_score=round(chunk.get("similarity_score", 0.0), 4),
        )
        for chunk in final_chunks
    ]

    # 8. Debug
    debug_info: DebugInfo | None = None
    if debug:
        chunk_index_map = {id(chunk): idx for idx, chunk in enumerate(retrieved_chunks)}

        debug_info = DebugInfo(
            retrieved_chunks=[_to_debug_chunk(c, score_map.get(i)) for i, c in enumerate(retrieved_chunks)],
            reranked_chunks=[_to_debug_chunk(c, score_map.get(chunk_index_map.get(id(c)))) for c in reranked_chunks],
            similarity_scores=[round(c.get("similarity_score", 0.0), 4) for c in retrieved_chunks],
            rerank_scores=[{"retrieval_index": i, "score": s} for i, s in sorted(score_map.items())],
            final_selected_chunks=[_to_debug_chunk(c, score_map.get(chunk_index_map.get(id(c)))) for c in final_chunks],
        )

    # Persist turn to session memory (only on successful, non-fallback responses)
    _save_to_session(session_id, question, answer)

    return QueryResponse(
        answer=answer,
        sources=sources,
        confidence=ConfidenceAssessment(
            score=confidence["score"],
            level=confidence["level"],
            reasoning=confidence["reasoning"],
        ),
        evaluation=evaluation,
        prompt_version=llm_result.get("prompt_version"),
        evaluation_prompt_version=evaluation.get("prompt_version"),
        debug=debug_info,
    )