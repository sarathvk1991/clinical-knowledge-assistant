import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import get_settings
from core.logging import logger
from core.errors import LLMError
from prompts.clinical_qa import (
    PROMPT_VERSION,
    CLINICAL_QA_SYSTEM_PROMPT,
    CLINICAL_QA_USER_TEMPLATE,
    format_context,
    format_conversation_history,
)

settings = get_settings()


def generate_answer(
    question: str,
    chunks: list[dict],
    conversation_history: list[dict] | None = None,
) -> dict:
    if not chunks:
        return {
            "answer": (
                "Based on the available documents, I cannot find sufficient "
                "information to answer this question."
            ),
            "sources_used": [],
            "confidence_note": "No relevant context was retrieved.",
        }

    try:
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.openai_api_key,
        )

        context_str = format_context(chunks)
        conv_str = format_conversation_history(conversation_history or [])

        user_message = CLINICAL_QA_USER_TEMPLATE.format(
            context=context_str,
            conversation_context=conv_str,
            question=question,
        )

        messages = [
            SystemMessage(content=CLINICAL_QA_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        content = content.strip()

        result = json.loads(content)
        result["prompt_version"] = PROMPT_VERSION
        logger.info("LLM response generated successfully")
        return result

    except json.JSONDecodeError:
        logger.warning("LLM returned non-JSON response, wrapping it")
        return {
            "answer": content,
            "sources_used": [],
            "confidence_note": "Response format was non-standard.",
        }
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise LLMError(str(e))
