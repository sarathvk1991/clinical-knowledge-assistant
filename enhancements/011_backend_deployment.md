Act as a senior backend engineer preparing a FastAPI application for production deployment on Render.

---

## Context

This is a GenAI backend with:
- FastAPI
- LangChain
- Pinecone
- OpenAI
- Modular service architecture

---

## Requirements

Prepare the backend for deployment.

### 1. Add production entrypoint
- Ensure uvicorn can run via:
  uvicorn main:app --host 0.0.0.0 --port $PORT

### 2. Create a start script (start.sh)
- Use bash
- Make it production-ready

### 3. Ensure requirements.txt includes:
- fastapi
- uvicorn
- langchain
- pinecone
- openai
- pydantic-settings

### 4. Add .env.example
Include:
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_ENV=

### 5. Ensure config.py reads env variables properly

### 6. Add CORS configuration (allow frontend)

### 7. Add /health endpoint if not already present

### 8. Ensure no blocking operations at import time

### 9. Add logging startup message

---

## Output

- Updated main.py (if needed)
- start.sh
- .env.example
- Any required changes clearly shown