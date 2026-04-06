from fastapi import APIRouter, UploadFile, File
from models.document import DocumentUploadResponse, DocumentListResponse
from models.common import StatusResponse
from services.document_service import upload_document, list_documents, delete_document

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    print(f"Received file: {file.filename}, size: {len(content)} bytes")
    return upload_document(
        filename=file.filename or "unknown",
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )


@router.get("", response_model=DocumentListResponse)
async def get_documents():
    docs = list_documents()
    return DocumentListResponse(documents=docs, total=len(docs))


@router.delete("/{document_id}", response_model=StatusResponse)
async def remove_document(document_id: str):
    delete_document(document_id)
    return StatusResponse(status="success", message=f"Document {document_id} deleted")
