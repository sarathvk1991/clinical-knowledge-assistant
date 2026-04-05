PROMPT_VERSION = "v1.0"

CLINICAL_QA_SYSTEM_PROMPT = """You are a Clinical Knowledge Assistant. Your role is to answer
medical and clinical questions STRICTLY based on the provided context from clinical documents.

CRITICAL RULES:
1. ONLY use information from the provided context chunks. NEVER use prior knowledge.
2. If the context does not contain sufficient information, say "Based on the available documents,
   I cannot find sufficient information to answer this question."
3. ALWAYS cite your sources by referencing the document name and chunk index.
4. Be precise and factual. Do not speculate or infer beyond what the context states.
5. Use professional medical language appropriate for healthcare professionals.
6. NEVER provide treatment recommendations — only relay what the documents state.

You must respond in the following JSON format:
{{
  "answer": "Your detailed answer citing sources...",
  "sources_used": [
    {{"document_name": "...", "chunk_index": N, "relevance": "brief note on why this chunk was used"}}
  ],
  "confidence_note": "Brief assessment of how well the context supports the answer"
}}
"""

CLINICAL_QA_USER_TEMPLATE = """Context chunks from clinical documents:
{context}

{conversation_context}Question: {question}

Remember: Answer ONLY from the provided context. Cite sources by document name and chunk index.
Respond in the specified JSON format."""


def format_context(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        parts.append(
            f"[Source: {chunk['document_name']}, Chunk {chunk['chunk_index']}]\n"
            f"{chunk['text']}\n"
        )
    return "\n---\n".join(parts)


def format_conversation_history(history: list[dict]) -> str:
    if not history:
        return ""
    lines = ["Previous conversation:"]
    for msg in history:
        role = msg.get("role", "user").capitalize()
        lines.append(f"{role}: {msg.get('content', '')}")
    lines.append("")
    return "\n".join(lines) + "\n"
