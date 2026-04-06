from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from core.errors import AppError, app_error_handler
from core.middleware import RequestIdMiddleware
from core.logging import logger
from api.documents import router as documents_router
from api.query import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting Clinical Knowledge Assistant", extra={"env": settings.app_env})
    yield
    logger.info("Shutting down Clinical Knowledge Assistant")


app = FastAPI(
    title="Clinical Knowledge Assistant",
    description="Healthcare RAG system with medical safety and explainability",
    version="1.0.0",
    lifespan=lifespan,
)

_settings = get_settings()

if _settings.frontend_url == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [_settings.frontend_url]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(query_router, prefix="/api", tags=["query"])


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/debug/pinecone")
def debug_pinecone():
    from pinecone import Pinecone
    from config import get_settings
    from services.embedding_service import generate_embedding

    settings = get_settings()

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)

    response = {}

    try:
        stats = index.describe_index_stats()
        response["total_vector_count"] = stats.get("total_vector_count", 0)
    except Exception as e:
        response["stats_error"] = str(e)

    try:
        test_query = "hypertension treatment"
        query_vector = generate_embedding(test_query)

        result = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )

        # ✅ SAFE SERIALIZATION
        response["query_match_count"] = len(result.get("matches", []))
        response["matches"] = [
            {
                "score": m.get("score"),
                "metadata": m.get("metadata", {})
            }
            for m in result.get("matches", [])
        ]

    except Exception as e:
        response["query_error"] = str(e)

    return response