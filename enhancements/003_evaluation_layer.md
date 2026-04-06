Act as a senior backend engineer.

Create a simple evaluation service for the existing RAG system.

---

## Goal

Evaluate whether an LLM-generated answer is grounded in retrieved context.

---

## Function

evaluate_answer(query: str, answer: str, chunks: List[dict]) -> dict

---

## Requirements

1. Use LLM to evaluate answer quality based on provided chunks

2. Evaluate:
- grounded (boolean): is answer supported by chunks?
- hallucination (boolean): does answer include unsupported claims?
- score (float 0–1): overall quality
- reasoning (short explanation)

---

## Prompt Rules

- Only consider provided chunks as truth
- If answer contains info not in chunks → hallucination = true
- If answer is well supported → grounded = true
- Keep reasoning short (1–2 lines)

---

## Output format (strict JSON)

{
  "grounded": true/false,
  "hallucination": true/false,
  "score": float,
  "reasoning": "..."
}

---

## Implementation Constraints

- Use existing LLM setup (ChatOpenAI)
- Temperature = 0
- Keep token usage low
- Handle JSON parsing safely
- Add fallback if evaluation fails

---

## Generate

- evaluation_service.py
- evaluation prompt template