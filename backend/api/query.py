from fastapi import APIRouter
from models.query import QueryRequest, QueryResponse
from services.query_service import process_query

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    return process_query(
        question=request.question,
        document_filter=request.document_filter,
        top_k=request.top_k,
        conversation_history=[
            msg.model_dump() for msg in request.conversation_history
        ],
        debug=request.debug,
        session_id=request.session_id,
    )
