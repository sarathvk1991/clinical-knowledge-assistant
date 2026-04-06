You are an expert senior software engineer, AI architect, and backend/frontend system designer.

Your task is to design and implement a **production-ready Clinical Knowledge Assistant**, a healthcare AI system built using Retrieval-Augmented Generation (RAG).

The system must strictly follow **safety, grounding, and explainability principles** suitable for healthcare use cases.

---

# 🚨 Core Principles (MANDATORY)

1. **Zero Hallucination Policy**

   * Only answer using retrieved document context
   * Do NOT infer beyond provided data
   * If insufficient context → return fallback response

2. **Medical Safety Compliance**

   * Always include a disclaimer in every response
   * Avoid diagnostic or prescriptive medical advice
   * Clearly indicate uncertainty when present

3. **Explainability First**

   * Every answer must include:

     * Source citations (document + chunk reference)
     * Confidence score
     * Traceability to retrieved chunks

---

# 🧠 Functional Requirements

## Document Management

* Upload medical/clinical documents (PDF, TXT)
* Store metadata:

  * id, name, type, upload_date
* List uploaded documents
* Delete documents
* Update/re-upload documents

## RAG-based Query System

* Accept natural language queries
* Retrieve relevant document chunks (Top-K)
* Support metadata-based filtering (e.g., document type)
* Generate grounded answers using LLM

## Response Format (STRICT)

Each response must include:

* answer (grounded)
* sources (document + chunk references)
* confidence_score (heuristic-based)
* disclaimer
* fallback message if needed

## Conversational Support

* Allow re-asking/refinement of previous queries
* Maintain minimal conversational continuity

## System Observability

* Show ingestion status (success/failure)
* Show query processing status
* Log errors and failures

---

# 🔁 System Flow

1. User uploads document
2. System:

   * Parses document
   * Splits into chunks
   * Generates embeddings
3. Store chunks in vector DB (with metadata)
4. User submits query
5. Retrieve Top-K relevant chunks (+ filters)
6. Pass context to LLM
7. Generate structured response
8. Return:

   * answer
   * sources
   * confidence
   * disclaimer

---

# 🏗️ Architecture (MANDATORY)

## Backend (Python + FastAPI)

### Layered Design

1. **API Layer**

   * FastAPI routers
   * Request/response validation (Pydantic)

2. **Service Layer**

   * DocumentService
   * QueryService
   * RetrievalService
   * LLMService
   * EmbeddingService

3. **Data Layer**

   * Pinecone integration
   * Metadata handling
   * Vector operations

4. **Infrastructure Layer**

   * Logging
   * Config management
   * Error handling

---

## APIs

* POST `/documents/upload`
* GET `/documents`
* DELETE `/documents/{id}`
* POST `/query`

---

## Data Models

Document:

* id
* name
* type
* upload_date

Chunk:

* id
* document_id
* text
* embedding
* metadata

Query:

* query_text
* filters

Response:

* answer
* sources
* confidence_score
* disclaimer

---

# ⚙️ GenAI Layer (LangChain आधारित)

## Responsibilities

* Document loading
* Chunking strategy
* Embedding generation
* Retrieval pipeline
* Prompt orchestration

## Prompt Rules (STRICT)

* Only use retrieved context
* Cite sources explicitly
* No speculation
* Return structured output (JSON format)

---

# 🧮 Confidence Score Logic

Must be heuristic-based using:

* Retrieval similarity scores
* Number of supporting chunks
* Consistency of sources

Return:

* High / Medium / Low OR numeric score (0–1)

---

# 🗄️ Vector Database

Use Pinecone:

* Store embeddings + metadata:

  * document_id
  * chunk_id
  * document_type

Support:

* Top-K retrieval
* Metadata filtering

---

# ⚡ Performance & Scalability

* Async FastAPI endpoints
* Batch embedding generation
* Efficient retrieval for large datasets
* Optional caching (Redis/in-memory)
* Handle concurrent users

---

# 📊 Logging & Observability

* Structured JSON logging
* Include:

  * request_id
  * query
  * retrieved chunks
  * LLM response
* Debug RAG failures:

  * Retrieval issue vs Generation issue

---

# ❌ Error Handling

Handle:

* Invalid uploads
* Parsing failures
* Embedding failures
* LLM timeouts

Return clear API errors

---

# 🧩 Extensibility

Design for:

* Future LangGraph agent workflows
* LLM provider abstraction (OpenAI, etc.)
* Evaluation pipelines (LLMOps)

---

# ⚛️ Frontend (React)

Minimal UI:

Components:

* Document upload
* Document list
* Query input box
* Response display:

  * answer
  * sources
  * confidence
  * disclaimer

Use REST APIs for communication

---

# ⚙️ Configuration

* Environment-based config (.env)
* Central config module
* Configurable:

  * LLM provider
  * Vector DB
  * Chunking strategy

---

# 🧪 Testing & Maintainability

* Modular design
* Unit-testable services
* Clear separation of concerns
* Dependency injection where applicable

---

# 🚫 Non-Goals

* Not a replacement for medical professionals
* Not for real-time clinical decisions
* No EMR integration (initial version)
* Minimal UI only

---

# 📦 Deliverables

Generate:

1. Full project structure
2. Backend implementation (FastAPI)
3. LangChain RAG pipeline
4. Pinecone integration
5. Prompt templates
6. Confidence scoring logic
7. Logging setup
8. React frontend (minimal)
9. Example API requests/responses
10. Setup instructions

---

# 🧠 Output Expectations

* Clean, modular, production-grade code
* Well-structured folders
* Clear separation of concerns
* Extensible design
* Strong emphasis on safety and explainability

---

Build this system step-by-step with clean architecture and production readiness in mind.
