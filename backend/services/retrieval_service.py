from pinecone import Pinecone

from config import get_settings
from core.logging import logger
from core.errors import RetrievalError
from services.embedding_service import generate_embedding

settings = get_settings()

def get_pinecone_client():
    return Pinecone(api_key=settings.pinecone_api_key)


def retrieve_chunks(
    query: str,
    top_k: int | None = None,
    document_filter: list[str] | None = None,
) -> list[dict]:
    k = top_k or settings.retrieval_top_k

    try:
        query_embedding = generate_embedding(query)
        pc = get_pinecone_client()
        index = pc.Index(settings.pinecone_index_name)

        filter_dict = {}
        if document_filter:
            filter_dict["document_id"] = {"$in": document_filter}

        results = index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None,
        )

        chunks = []
        for match in results.matches:
            chunks.append({
                "text": match.metadata.get("text", ""),
                "document_name": match.metadata.get("document_name", ""),
                "document_id": match.metadata.get("document_id", ""),
                "chunk_index": match.metadata.get("chunk_index", 0),
                "similarity_score": match.score,
            })

        logger.info(f"Retrieved {len(chunks)} chunks for query")
        return chunks

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise RetrievalError(str(e))
