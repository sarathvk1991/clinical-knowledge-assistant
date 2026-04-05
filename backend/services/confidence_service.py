import statistics


def compute_confidence(chunks: list[dict]) -> dict:
    if not chunks:
        return {
            "score": 0.0,
            "level": "no_evidence",
            "reasoning": "No relevant chunks were retrieved from the knowledge base.",
        }

    scores = [c["similarity_score"] for c in chunks]
    n = len(scores)
    top_score = max(scores)

    # --- Component 1: average similarity (0–1) ---
    avg_similarity = sum(scores) / n

    # --- Component 2: chunk count score — more supporting chunks = higher score (cap at 5) ---
    chunk_count_score = min(n / 5.0, 1.0)

    # --- Component 3: variance score — low variance means consistent retrieval quality ---
    if n > 1:
        variance = statistics.variance(scores)
    else:
        variance = 0.0
    # Invert variance: high variance → low score. Scale factor of 10 keeps it in [0, 1] range.
    variance_score = max(0.0, 1.0 - variance * 10)

    # --- Component 4: agreement score — fraction of chunks within 0.1 of the top score ---
    agreement_score = sum(1 for s in scores if top_score - s <= 0.1) / n

    # --- Final weighted score ---
    score = (
        0.4 * avg_similarity
        + 0.2 * chunk_count_score
        + 0.2 * variance_score
        + 0.2 * agreement_score
    )
    score = round(max(0.0, min(1.0, score)), 3)

    # --- Level mapping ---
    if score >= 0.75:
        level = "high"
    elif score >= 0.4:
        level = "medium"
    else:
        level = "low"

    reasoning = (
        f"{level.capitalize()} confidence: {n} chunk(s) retrieved, "
        f"avg similarity {avg_similarity:.2f}, "
        f"variance {variance:.4f}, "
        f"agreement {agreement_score:.2f}."
    )

    return {"score": score, "level": level, "reasoning": reasoning}
