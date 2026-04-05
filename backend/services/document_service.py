import uuid
from datetime import datetime, timezone
from io import BytesIO

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone

from config import get_settings
from core.logging import logger
from core.errors import DocumentParsingError, DocumentNotFoundError
from models.document import DocumentMetadata, DocumentUploadResponse
from services.embedding_service import generate_embeddings

settings = get_settings()
def get_pinecone_client():
    return Pinecone(api_key=settings.pinecone_api_key)


def _get_index():
    pc = get_pinecone_client()
    return pc.Index(settings.pinecone_index_name)


def _parse_text_file(content: bytes, filename: str) -> list[str]:
    text = content.decode("utf-8")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def _parse_pdf_file(content: bytes, filename: str) -> list[str]:
    import tempfile
    import os

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        full_text = "\n\n".join(page.page_content for page in pages)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(full_text)
    except Exception as e:
        raise DocumentParsingError(str(e))
    finally:
        if "tmp_path" in locals():
            os.unlink(tmp_path)


def upload_document(filename: str, content: bytes, content_type: str) -> DocumentUploadResponse:
    document_id = str(uuid.uuid4())
    upload_date = datetime.now(timezone.utc).isoformat()

    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        chunks = _parse_pdf_file(content, filename)
        doc_type = "pdf"
    elif content_type in ("text/plain",) or filename.lower().endswith(".txt"):
        chunks = _parse_text_file(content, filename)
        doc_type = "txt"
    else:
        raise DocumentParsingError(f"Unsupported file type: {content_type}")

    if not chunks:
        raise DocumentParsingError("No content extracted from document")

    embeddings = generate_embeddings(chunks)

    index = _get_index()
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{document_id}_{i}",
            "values": embedding,
            "metadata": {
                "document_id": document_id,
                "document_name": filename,
                "document_type": doc_type,
                "upload_date": upload_date,
                "chunk_index": i,
                "chunk_count": len(chunks),
                "text": chunk,
            },
        })

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i : i + batch_size])

    logger.info(f"Uploaded document {filename} with {len(chunks)} chunks")

    return DocumentUploadResponse(
        document_id=document_id,
        document_name=filename,
        chunk_count=len(chunks),
        message=f"Document '{filename}' uploaded successfully with {len(chunks)} chunks",
    )


def list_documents() -> list[DocumentMetadata]:
    index = _get_index()
    stats = index.describe_index_stats()

    if stats.total_vector_count == 0:
        return []

    # Query with a zero vector to list documents, fetching metadata
    dummy_vector = [0.0] * settings.embedding_dimension
    results = index.query(
        vector=dummy_vector,
        top_k=10000,
        include_metadata=True,
        filter={"chunk_index": {"$eq": 0}},
    )

    documents: dict[str, DocumentMetadata] = {}
    for match in results.matches:
        meta = match.metadata
        doc_id = meta.get("document_id", "")
        if doc_id not in documents:
            documents[doc_id] = DocumentMetadata(
                document_id=doc_id,
                document_name=meta.get("document_name", ""),
                document_type=meta.get("document_type", ""),
                upload_date=meta.get("upload_date", ""),
                chunk_count=meta.get("chunk_count", 0),
            )

    return list(documents.values())


def delete_document(document_id: str) -> None:
    index = _get_index()

    # Find all chunks for this document
    dummy_vector = [0.0] * settings.embedding_dimension
    results = index.query(
        vector=dummy_vector,
        top_k=10000,
        include_metadata=True,
        filter={"document_id": {"$eq": document_id}},
    )

    if not results.matches:
        raise DocumentNotFoundError(document_id)

    ids_to_delete = [match.id for match in results.matches]
    batch_size = 1000
    for i in range(0, len(ids_to_delete), batch_size):
        index.delete(ids=ids_to_delete[i : i + batch_size])

    logger.info(f"Deleted document {document_id} ({len(ids_to_delete)} chunks)")
