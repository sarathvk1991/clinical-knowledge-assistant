from unittest.mock import patch, MagicMock
from services.document_service import _parse_text_file
from core.errors import DocumentParsingError
import pytest


def test_parse_text_file_splits_content():
    content = ("This is a test document. " * 100).encode("utf-8")
    chunks = _parse_text_file(content, "test.txt")
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_parse_text_file_empty():
    content = b""
    chunks = _parse_text_file(content, "test.txt")
    assert len(chunks) == 0


def test_parse_text_file_small_content():
    content = b"Small content."
    chunks = _parse_text_file(content, "test.txt")
    assert len(chunks) == 1
    assert chunks[0] == "Small content."


@patch("services.document_service.generate_embeddings")
@patch("services.document_service._get_index")
def test_upload_document_unsupported_type(mock_index, mock_embed):
    from services.document_service import upload_document

    with pytest.raises(DocumentParsingError, match="Unsupported file type"):
        upload_document("file.xyz", b"data", "application/xyz")


@patch("services.document_service.generate_embeddings")
@patch("services.document_service._get_index")
def test_upload_document_txt(mock_index, mock_embed):
    from services.document_service import upload_document

    mock_embed.return_value = [[0.1] * 1536]
    mock_idx = MagicMock()
    mock_index.return_value = mock_idx

    result = upload_document("test.txt", b"Hello world content here.", "text/plain")
    assert result.document_name == "test.txt"
    assert result.chunk_count >= 1
    mock_idx.upsert.assert_called_once()
