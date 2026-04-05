import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import get_settings
from core.logging import logger
from prompts.evaluation import (
    EVALUATION_PROMPT_VERSION,
    EVALUATION_SYSTEM_PROMPT,
    EVALUATION_USER_TEMPLATE,
    format_chunks_for_eval,
)

settings = get_settings()

_FALLBACK: dict = {
    "grounded": False,
    "hallucination": True,  # ✅ safer default
    "score": 0.0,
    "reasoning": "Evaluation failed, unable to verify answer.",
}


def evaluate_answer(query: str, answer: str, chunks: list[dict]) -> dict:
    """Evaluate whether the LLM answer is grounded in the retrieved chunks.

    Returns a dict with keys: grounded, hallucination, score, reasoning.
    Falls back to a safe default if the LLM call or JSON parsing fails.
    """
    if not chunks or not answer:
        return {**_FALLBACK, "reasoning": "Missing answer or context chunks — evaluation skipped."}

    MAX_EVAL_CHUNKS = 5
    chunks = chunks[:MAX_EVAL_CHUNKS]
    try:
        logger.debug(
            "Evaluation input",
            extra={
                "query": query[:100],
                "answer": answer[:200],
                "num_chunks": len(chunks),
            },
        )
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.0,
            max_tokens=200,
            api_key=settings.openai_api_key,
            request_timeout=5,
        )

        user_message = EVALUATION_USER_TEMPLATE.format(
            query=query,
            chunks=format_chunks_for_eval(chunks),
            answer=answer,
        )

        response = llm.invoke([
            SystemMessage(content=EVALUATION_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]

        result = json.loads(content.strip())

        if not result:
            logger.warning("Empty evaluation result, using fallback")
            return _FALLBACK.copy()
        
        score = float(result.get("score", 0.0))
        if score > 1:
            score = score / 10.0

        evaluation = {
            "grounded": bool(result.get("grounded", False)),
            "hallucination": bool(result.get("hallucination", False)),
            "score": max(0.0, min(score, 1.0)),
            "reasoning": str(result.get("reasoning", "No reasoning provided")),
            "prompt_version": EVALUATION_PROMPT_VERSION,
        }

        logger.info(
            "Answer evaluation complete",
            extra={"evaluation": evaluation},
        )
        return evaluation

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.warning("Evaluation parse error (%s); returning fallback", e)
        return _FALLBACK.copy()
    except Exception as e:
        logger.error("Evaluation failed unexpectedly: %s", e)
        return _FALLBACK.copy()
