import json
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import get_settings
from core.logging import logger

settings = get_settings()

MAX_CANDIDATES = 15  # safeguard for future scaling

# TODO: Replace LLM-based reranking with cross-encoder or external rerank API for lower latency

def truncate_text(text: str, max_len: int = 400) -> str:
    """Truncate text without cutting words abruptly."""
    truncated = text[:max_len]
    return truncated.rsplit(" ", 1)[0] if " " in truncated else truncated

_RERANK_SYSTEM_PROMPT = (
    "You are a clinical relevance judge. Given a user query and a list of text chunks, "
    "score each chunk's relevance to the query on a scale of 0–10. "
    "Prefer factual correctness and direct clinical relevance over mere semantic similarity. "
    "Return ONLY a JSON array of objects with keys 'index' (int) and 'score' (float 0–10). "
    "No explanation, no markdown, just the JSON array. "
    "Do NOT reward vague or partially related matches. "
    "Penalize redundant or repetitive chunks."
)

_RERANK_USER_TEMPLATE = """\
Query: {query}

Chunks:
{chunks}

Return a JSON array: [{{"index": 0, "score": 8.5}}, ...]"""


def rerank(query: str, chunks: list[dict], top_k: int | None = None) -> Tuple[List[Dict], Dict[int, float]]:
    """Score and reorder chunks by relevance to query, returning the top_k most relevant."""
    if not chunks:
        return chunks, {}

    # Apply candidate cap for safety
    chunks = chunks[:MAX_CANDIDATES]

    k = top_k if top_k is not None else settings.rerank_top_k

    logger.info(
        "Reranking %d chunks",
        len(chunks),
        extra={"pre_rerank_chunks": [c.get("chunk_index") for c in chunks]},
    )

    chunks_text = "\n\n".join(
        f"[{i}] {truncate_text(chunk['text'])}"
        for i, chunk in enumerate(chunks)
    )

    try:
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.0,
            max_tokens=256,
            api_key=settings.openai_api_key,
            request_timeout=5,
        )

        user_message = _RERANK_USER_TEMPLATE.format(
            query=query,
            chunks=chunks_text,
        )

        response = llm.invoke([
            SystemMessage(content=_RERANK_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]

        scores = json.loads(content.strip())
        
        # Normalize scores to 0–1 range
        score_map: Dict[int, float] = {}

        for item in scores:
            try:
                idx = int(item["index"])
                score = float(item["score"]) / 10.0
                score_map[idx] = max(0.0, min(score, 1.0))
            except Exception:
                continue
            
        if not score_map:
            logger.warning("Empty score_map from reranker, falling back")
            return chunks[:k], {}

        logger.info(
            "Reranker scores: %s",
            score_map,
            extra={
                "rerank_scores": [
                    {"chunk_index": idx, "score": score}
                    for idx, score in score_map.items()
                ]
            },
        )

        ranked = sorted(
            enumerate(chunks),
            key=lambda pair: score_map.get(pair[0], 0.0),
            reverse=True,
        )
        
        effective_k = min(k, len(chunks))
        reranked = [chunk for _, chunk in ranked[:effective_k]]

        logger.info(
            "Reranked order (chunk_index): %s",
            [c.get("chunk_index") for c in reranked],
        )
        return reranked, score_map

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Reranker failed to parse LLM output (%s); returning original order", e)
        return chunks[:k], {}
    except Exception as e:
        logger.error("Reranker encountered an unexpected error: %s", e)
        return chunks[:k], {}
