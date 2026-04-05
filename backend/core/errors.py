from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundError(AppError):
    def __init__(self, document_id: str):
        super().__init__(f"Document not found: {document_id}", 404)


class DocumentParsingError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"Failed to parse document: {detail}", 422)


class EmbeddingError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"Embedding generation failed: {detail}", 502)


class RetrievalError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"Retrieval failed: {detail}", 502)


class LLMError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"LLM generation failed: {detail}", 502)


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": type(exc).__name__},
    )
