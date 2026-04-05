# Clinical Knowledge Assistant

A production-ready healthcare RAG (Retrieval-Augmented Generation) system with medical safety, zero-hallucination enforcement, and source attribution.

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / LangChain / Pinecone / OpenAI (GPT-4o)
- **Frontend**: Vite + React + TypeScript
- **Infrastructure**: Docker + docker-compose

## Quick Start

1. **Clone and configure**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Create Pinecone index**: Create an index named `clinical-knowledge` with model `text-embedding-3-small`, dimension `1536` and `cosine` metric in your Pinecone dashboard.

3. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

4. **Access**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

1. Upload clinical PDF or TXT documents via the UI
2. Ask clinical questions — the system retrieves relevant chunks, generates grounded answers with source citations, and provides confidence scoring
3. Every response includes a medical disclaimer

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## Key Features

- **Zero-hallucination**: LLM is strictly instructed to only use provided context
- **Source attribution**: Every answer cites specific document chunks
- **Confidence scoring**: Heuristic scoring based on similarity, chunk count, and consistency
- **Medical safety**: Mandatory disclaimers and refusal to provide treatment recommendations
