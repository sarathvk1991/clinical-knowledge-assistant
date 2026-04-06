Act as a senior FastAPI backend engineer.

Generate API tests for a GenAI system.

---

## Context

FastAPI app has endpoints:

- POST /query
- POST /documents/upload
- GET /documents
- DELETE /documents/{id}

---

## Requirements

- Use pytest
- Use FastAPI TestClient
- Mock service layer (do NOT call real services)

---

## 1. Query API

Create: tests/api/test_query_api.py

Test cases:

1. Valid request → 200 response
2. Missing question → 422 validation error
3. Debug flag → debug present in response
4. Session_id supported
5. Mock process_query

---

## 2. Documents API

Create: tests/api/test_documents_api.py

Test cases:

1. Upload document → success response
2. List documents → returns list
3. Delete document → success
4. Invalid delete → error handled

---

## Output

Generate complete test files with proper mocking.