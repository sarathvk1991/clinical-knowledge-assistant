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
        enriched_query = f"{query} clinical guidelines treatment diagnosis management"
        query_embedding = generate_embedding(enriched_query.lower())
        pc = get_pinecone_client()
        index = pc.Index(settings.pinecone_index_name)

        filter_dict = {}
        if document_filter:
            filter_dict["document_id"] = {"$in": document_filter}

        query_params = {
             "vector": query_embedding,
             "top_k": k,
             "include_metadata": True,
        }
        
        if filter_dict:
             query_params["filter"] = filter_dict
             
        results = index.query(**query_params)
        

        chunks = []

        matches = results.get("matches", [])
        
        for match in matches:
            metadata = match.get("metadata", {})
            chunks.append({
                "text": metadata.get("text", ""),
                "document_name": metadata.get("document_name", ""),
                "document_id": metadata.get("document_id", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "similarity_score": match.get("score", 0.0),
            })

        logger.info(f"Retrieved {len(chunks)} chunks for query")
        return chunks

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise RetrievalError(str(e))
