# Clinical Knowledge Assistant

> A production-grade, healthcare-focused RAG system that answers clinical questions grounded strictly in uploaded documents — with LLM-based reranking, hallucination detection, confidence scoring, and full pipeline observability.

---

## Overview

Clinical Knowledge Assistant is an end-to-end **Retrieval-Augmented Generation (RAG)** application built for the healthcare domain. Clinicians and researchers upload PDF or plain-text clinical documents; the system chunks, embeds, and indexes them in a vector database. Natural language questions are answered by a multi-stage pipeline: semantic retrieval → LLM-based reranking → GPT-4o generation → LLM-based hallucination evaluation → heuristic confidence scoring.

Every response cites its sources with similarity scores, carries a confidence level, and is prefixed with a caution notice when the pipeline detects low confidence or a potential hallucination. A debug mode exposes every intermediate stage of the pipeline for full explainability.

---

## Key Features

### Core RAG Pipeline
- Upload PDF or TXT clinical documents via drag-and-drop or file picker
- Automatic chunking (configurable size / overlap) and embedding via `text-embedding-3-small`
- Semantic retrieval from Pinecone with top-K pre-fetch
- **LLM-based reranker** — GPT-4o rescores retrieved chunks for query relevance before generation
- **GPT-4o generation** — answers grounded strictly in retrieved context; model is instructed never to use prior knowledge

### Safety & Reliability
- **LLM-based hallucination evaluator** — a second GPT-4o call grades the answer for groundedness and flags hallucinations
- **Heuristic confidence scoring** — four-component weighted score (avg similarity, chunk count, variance, agreement) maps to `high / medium / low / no_evidence`
- **Graceful failure handling** — fallback response when no chunks are retrieved, LLM fails, or answer is empty
- **Cautious response prefix** when hallucination is detected or confidence < 0.4
- Medical disclaimer appended to every response

### Observability & Explainability
- **Debug mode toggle** in the UI — exposes retrieved chunks, reranked chunks, final selected chunks, and all scores
- **Prompt versioning** — `PROMPT_VERSION` tracked on every response for auditability
- Structured JSON logging (python-json-logger) with per-request metadata
- Evaluation result and prompt version returned in API response

### Conversational Memory
- Session-based in-memory conversation history (last 3 turns / 6 messages)
- Session ID passed per request; history injected into generation prompt automatically

### Developer Experience
- One-command local stack via Docker Compose (backend + frontend)
- **Load Sample Medical Data** button seeds the demo with a pre-built clinical guidelines document
- Hot-reload on both backend (uvicorn) and frontend (Vite)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React + TypeScript                        │
│  DocumentUpload │ DocumentList │ QueryInput │ ResponseDisplay    │
│                    Debug Panel (collapsible)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /api/query
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│                                                                  │
│  1. RetrievalService  ──►  Pinecone (top-10 ANN search)         │
│                                                                  │
│  2. RerankerService   ──►  GPT-4o (score each chunk 0–1)        │
│                            └─► top-K reranked chunks            │
│                                                                  │
│  3. ConfidenceService ──►  Heuristic score (similarity,         │
│                            count, variance, agreement)           │
│                                                                  │
│  4. LLMService        ──►  GPT-4o (generate grounded answer)    │
│                            Prompt v1.0 — JSON response           │
│                                                                  │
│  5. EvaluationService ──►  GPT-4o (hallucination check)         │
│                            └─► cautious prefix if flagged        │
│                                                                  │
│  6. QueryService      ──►  Assemble QueryResponse               │
│                            (answer, sources, confidence,         │
│                             evaluation, debug, prompt_version)   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Embeddings
                            ▼
                    ┌───────────────┐
                    │   Pinecone    │
                    │ Vector Index  │
                    └───────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn |
| **LLM & Embeddings** | OpenAI GPT-4o, `text-embedding-3-small` (1536-dim) |
| **RAG Framework** | LangChain (text splitters, Pinecone integration) |
| **Vector Database** | Pinecone |
| **Document Parsing** | pypdf |
| **Logging** | python-json-logger (structured JSON) |
| **Testing** | pytest, pytest-asyncio, pytest-mock, httpx |
| **Infrastructure** | Docker, Docker Compose |
| **Deployment** | Render (backend), Vercel (frontend) |

---

## Project Structure

```
clinical-knowledge-assistant/
├── backend/
│   ├── api/
│   │   ├── documents.py          # Upload, list, delete endpoints
│   │   └── query.py              # POST /api/query
│   ├── core/
│   │   ├── errors.py             # Custom exception types
│   │   ├── logging.py            # Structured JSON logger
│   │   └── middleware.py         # CORS, request logging
│   ├── models/
│   │   ├── document.py           # Document Pydantic models
│   │   └── query.py              # QueryRequest, QueryResponse, DebugInfo
│   ├── prompts/
│   │   ├── clinical_qa.py        # Generation prompt + version (v1.0)
│   │   └── evaluation.py         # Hallucination evaluation prompt
│   ├── services/
│   │   ├── query_service.py      # Orchestrates full RAG pipeline
│   │   ├── retrieval_service.py  # Pinecone ANN search
│   │   ├── reranker_service.py   # LLM-based chunk reranking
│   │   ├── llm_service.py        # GPT-4o generation
│   │   ├── evaluation_service.py # Hallucination detection
│   │   ├── confidence_service.py # Heuristic confidence scoring
│   │   ├── embedding_service.py  # OpenAI embedding calls
│   │   └── document_service.py   # Chunking, embedding, upsert
│   ├── tests/
│   │   ├── unit/                 # ConfidenceService, EvaluationService, RerankerService
│   │   ├── api/                  # DocumentsAPI, QueryAPI endpoint tests
│   │   └── integration/          # QueryService end-to-end tests
│   ├── config.py                 # Pydantic-settings config
│   ├── main.py                   # FastAPI app factory
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── sample_medical_guidelines.txt  # Demo seed document
│   ├── src/
│   │   ├── api/client.ts             # Typed fetch wrappers
│   │   ├── components/
│   │   │   ├── DocumentUpload.tsx    # Drag-drop + sample loader button
│   │   │   ├── DocumentList.tsx      # List + delete documents
│   │   │   ├── QueryInput.tsx        # Question form + debug toggle
│   │   │   ├── ResponseDisplay.tsx   # Answer + sources + debug panel
│   │   │   └── StatusBar.tsx         # Backend health indicator
│   │   ├── types/index.ts            # Shared TypeScript interfaces
│   │   └── styles/index.css
│   ├── Dockerfile
│   └── vite.config.ts
├── docker-compose.yml
└── .env.example
```

---

## Running Locally

### Prerequisites
- Docker Desktop
- OpenAI API key (GPT-4o access)
- Pinecone account + index named `clinical-knowledge` (dimension: 1536, metric: cosine)

### 1. Clone and configure

```bash
git clone <repo-url>
cd clinical-knowledge-assistant
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=clinical-knowledge
PINECONE_ENVIRONMENT=us-east-1
```

### 2. Start the stack

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### 3. Try the demo

1. Click **Load Sample Medical Data** to seed a clinical guidelines document instantly.
2. Ask a question: *"What is the first-line treatment for hypertension?"*
3. Enable **Show Debug Info** to inspect retrieved, reranked, and final chunks with scores.

### Running without Docker

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

---

## Deployment

### Backend → Render

1. Create a new **Web Service** pointing to `backend/`
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from `.env.example` in the Render dashboard
5. Set `FRONTEND_URL` to your Vercel deployment URL

### Frontend → Vercel

1. Set root directory to `frontend/`
2. Add environment variable: `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`
3. Build command: `npm run build` | Output directory: `dist/`

---

## Testing Strategy

Tests are organized in three layers:

```
tests/
├── unit/           # Pure logic, no I/O — ConfidenceService, EvaluationService, RerankerService
├── api/            # FastAPI TestClient — endpoint contract tests with mocked services
└── integration/    # QueryService pipeline tests with mocked LLM/Pinecone calls
```

```bash
cd backend
pytest                        # all tests
pytest tests/unit/            # unit only
pytest tests/api/             # API contract tests
pytest tests/integration/     # pipeline integration tests
pytest -v --tb=short          # verbose output
```

Key design choices in tests:
- **No live API calls** — all OpenAI and Pinecone interactions are mocked via `pytest-mock`
- **Contract-level API tests** — verify request/response shapes, status codes, and error handling
- **Pipeline-level integration tests** — verify that `query_service` correctly orchestrates reranking, confidence, generation, and evaluation stages

---

## Example Output

**Question:** *"What is the recommended HbA1c target for adults with type 2 diabetes?"*

```json
{
  "answer": "According to the ADA 2023 guidelines [sample_medical_guidelines.txt, Chunk 3], the recommended HbA1c target for most non-pregnant adults with type 2 diabetes is less than 7.0% (53 mmol/mol).",
  "sources": [
    {
      "document_name": "sample_medical_guidelines.txt",
      "chunk_index": 3,
      "text_excerpt": "HbA1c: <7.0% for most non-pregnant adults...",
      "similarity_score": 0.9123
    }
  ],
  "confidence": {
    "score": 0.847,
    "level": "high",
    "reasoning": "High confidence: 5 chunk(s) retrieved, avg similarity 0.89, variance 0.0012, agreement 1.00."
  },
  "evaluation": {
    "grounded": true,
    "hallucination": false,
    "score": 0.95,
    "reasoning": "Answer is fully supported by the retrieved context."
  },
  "prompt_version": "v1.0",
  "disclaimer": "This information is for educational purposes only..."
}
```

**Debug mode** surfaces three collapsible panels:
- **Retrieved Chunks (10)** — raw ANN results with similarity scores
- **Reranked Chunks (5)** — GPT-4o relevance scores applied
- **Final Selected Chunks (5)** — what the LLM actually saw

---

## Key Design Decisions

**LLM-based reranking over BM25 / cross-encoder**
GPT-4o is prompted to score each chunk on a 0–1 relevance scale relative to the query. This leverages the LLM's clinical domain understanding rather than lexical overlap, yielding better precision on medical terminology without needing a fine-tuned cross-encoder.

**Separate evaluation pass for hallucination detection**
Generation and evaluation are split into two independent LLM calls. Asking a model to self-evaluate in the same call is unreliable; an independent call with only the retrieved context and the generated answer produces a more honest groundedness assessment.

**Heuristic confidence scoring as a complement to LLM evaluation**
LLM evaluation catches semantic hallucinations. The heuristic confidence score catches retrieval failures — low similarity, high variance, few supporting chunks. Both signals gate the cautious response prefix independently.

**Prompt versioning in the response contract**
`prompt_version` is returned in every `QueryResponse`, enabling offline analysis of answer quality across prompt iterations without relying on log grep. This reflects production thinking about iterating on LLM behavior safely.

**Session memory capped at 6 messages (3 turns)**
Unlimited history inflates the context window and dilutes retrieval relevance. Three turns preserves conversational coherence for follow-up questions while keeping prompts tight and costs predictable.

**Strict context grounding enforced at the system prompt level**
The generation prompt explicitly prohibits use of prior knowledge and requires structured JSON output with `sources_used`. This makes the model's reasoning auditable and reduces the surface area for hallucination.

---

## Future Enhancements

- [ ] Persistent session storage (Redis) for multi-instance deployments
- [ ] Document-level metadata filtering (date range, document type, specialty)
- [ ] Streaming responses via SSE for long-form answers
- [ ] Fine-grained chunk-level hallucination highlighting in the UI
- [ ] Automated regression tests comparing answer quality across prompt versions
- [ ] Role-based access control for multi-tenant clinical deployments
- [ ] Hybrid retrieval: dense (Pinecone) + sparse (BM25) with reciprocal rank fusion

---

## Why This Project Matters

Healthcare AI is one of the highest-stakes domains for RAG systems. A hallucinated drug dosage or fabricated guideline reference can directly harm patients. This project treats that seriously:

- **Two independent safety layers** (LLM hallucination evaluator + heuristic confidence) rather than trusting generation alone
- **Full pipeline transparency** — every intermediate result is inspectable via debug mode, which matters for clinical audit trails and regulatory defensibility
- **Strict grounding by design** — the system prompt architecture makes out-of-context answers structurally harder to produce, not just discouraged
- **Prompt versioning as a first-class concern** — reflects production thinking about iterating on LLM behavior safely at scale

The architecture reflects the judgment calls a GenAI architect makes when reliability and explainability are non-negotiable: separation of concerns across pipeline stages, multiple evaluation signals, observable intermediate state, and graceful degradation over silent failure.

---

## Author

Built as a portfolio project demonstrating production-grade GenAI system design for healthcare applications.

- **Architecture:** Multi-stage RAG with LLM-based reranking and evaluation
- **Stack:** FastAPI · GPT-4o · Pinecone · React · Docker
- **Focus:** Safety, explainability, and reliability in high-stakes AI domains
