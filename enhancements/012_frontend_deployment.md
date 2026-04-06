Act as a frontend engineer preparing a React (Vite) app for production deployment on Vercel.

---

## Context

Frontend communicates with a FastAPI backend.

---

## Requirements

1. Use environment variable:
   VITE_API_BASE_URL

2. Ensure all API calls use:
   import.meta.env.VITE_API_BASE_URL

3. Add fallback for local dev:
   http://localhost:8000

4. Ensure build works:
   npm run build

5. Add .env.example:
   VITE_API_BASE_URL=

6. Ensure no hardcoded URLs

7. Add simple error handling UI for API failures

---

## Output

- Updated API config file
- .env.example
- Any necessary code updates