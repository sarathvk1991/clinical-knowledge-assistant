from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "clinical-knowledge"
    pinecone_environment: str = "us-east-1"

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    backend_port: int = 8000
    # Set to your frontend's URL in production (e.g. https://my-app.onrender.com)
    frontend_url: str = "*"

    # Embedding
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # LLM
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 2048

    # Retrieval
    retrieval_top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Reranking
    rerank_enabled: bool = True
    rerank_top_k: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
