from openai import OpenAI
from config import get_settings
from core.logging import logger
from core.errors import EmbeddingError

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    try:
        batch_size = 100
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = client.embeddings.create(
                model=settings.embedding_model,
                input=batch,
            )
            all_embeddings.extend([item.embedding for item in response.data])

        logger.info(f"Generated embeddings for {len(texts)} texts")
        return all_embeddings

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise EmbeddingError(str(e))


def generate_embedding(text: str) -> list[float]:
    result = generate_embeddings([text])
    return result[0]
