EVALUATION_PROMPT_VERSION = "v1.0"

EVALUATION_SYSTEM_PROMPT = (
    "You are a clinical answer evaluator. "
    "You will be given a user query, an AI-generated answer, and the source chunks that were retrieved. "
    "Evaluate whether the answer is grounded in the provided chunks. "
    "RULES:\n"
    "- Treat the chunks as the only source of truth.\n"
    "- grounded=true if every factual claim in the answer is supported by at least one chunk.\n"
    "- hallucination=true if the answer contains any claim not found in the chunks.\n"
    "- score: float 0–1 reflecting overall answer quality and groundedness.\n"
    "- reasoning: 1–2 sentences explaining your verdict.\n"
    "Return ONLY a JSON object with keys: grounded, hallucination, score, reasoning. "
    "No markdown, no explanation outside the JSON."
)

EVALUATION_USER_TEMPLATE = """\
Query: {query}

Retrieved chunks:
{chunks}

Answer to evaluate:
{answer}

Return JSON: {{"grounded": true/false, "hallucination": true/false, "score": 0.0–1.0, "reasoning": "..."}}"""


def format_chunks_for_eval(chunks: list[dict], max_chars: int = 300) -> str:
    parts = []
    for chunk in chunks:
        text = chunk.get("text", "")
        if len(text) > max_chars:
            text = text[:max_chars].rsplit(" ", 1)[0] + "..."
        parts.append(f"[{chunk.get('document_name', '?')}, chunk {chunk.get('chunk_index', '?')}] {text}")
    return "\n\n".join(parts)
