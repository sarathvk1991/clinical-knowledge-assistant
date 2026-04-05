from unittest.mock import MagicMock, patch

import sys
    
mock_pinecone = MagicMock()
mock_pinecone.Pinecone = MagicMock()

sys.modules["pinecone"] = mock_pinecone
sys.modules["pinecone.control"] = MagicMock()
sys.modules["pinecone.config"] = MagicMock()

from services.query_service import process_query

@patch("services.query_service.evaluate_answer")
@patch("services.query_service.rerank")
@patch("services.query_service.generate_answer")
@patch("services.query_service.retrieve_chunks")
def test_process_query_returns_response(mock_retrieve, mock_generate, mock_rerank, mock_evaluate):
    mock_retrieve.return_value = [
        {
            "text": "Aspirin is used as an antiplatelet agent.",
            "document_name": "pharma_guide.pdf",
            "document_id": "doc-1",
            "chunk_index": 3,
            "similarity_score": 0.92,
        },
        {
            "text": "Common dose is 81mg daily for cardiac prophylaxis.",
            "document_name": "pharma_guide.pdf",
            "document_id": "doc-1",
            "chunk_index": 4,
            "similarity_score": 0.88,
        },
    ]
    mock_rerank.return_value = (mock_retrieve.return_value, {})
    
    mock_evaluate.return_value = {
        "grounded": True,
        "hallucination": False,
        "score": 0.9,
        "reasoning": "valid",
    }

    mock_generate.return_value = {
        "answer": "Aspirin is used as an antiplatelet agent at 81mg daily.",
        "sources_used": [{"document_name": "pharma_guide.pdf", "chunk_index": 3}],
        "confidence_note": "Well supported by context.",
    }

    result = process_query("What is aspirin used for?")

    assert result.answer == "Aspirin is used as an antiplatelet agent at 81mg daily."
    assert len(result.sources) == 2
    assert result.confidence.score > 0
    assert result.disclaimer


@patch("services.query_service.generate_answer")
@patch("services.query_service.retrieve_chunks")
def test_process_query_no_results(mock_retrieve, mock_llm):
    mock_retrieve.return_value = []
    mock_llm.return_value = {
        "answer": "Based on the available documents, I cannot find sufficient information.",
        "sources_used": [],
        "confidence_note": "No relevant context was retrieved.",
    }

    result = process_query("What is the meaning of life?")

    assert len(result.sources) == 0
    assert result.confidence.level == "low"
    assert result.confidence.score == 0.0
