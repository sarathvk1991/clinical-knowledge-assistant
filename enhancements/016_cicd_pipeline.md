You are a senior DevOps engineer.

I have a full-stack GenAI project with:

* Backend: FastAPI (Python)
* Frontend: React + Vite (TypeScript)
* Tests:

  * Backend: pytest
  * Frontend: (to be added)

I want to implement **CI/CD using GitHub Actions**.

---

## Requirements

Create a `.github/workflows/ci.yml` file with:

### 1. Backend Pipeline

* Use Python 3.11
* Install dependencies from backend/requirements.txt
* Run:
  pytest backend/

---

### 2. Frontend Pipeline

* Use Node.js (latest LTS)
* Install dependencies from frontend/
* Run:
  npm install
  npm run build

(Tests will be added later — prepare structure for it)

---

### 3. General Requirements

* Run on:

  * push
  * pull_request

* Fail pipeline if:

  * tests fail
  * build fails

* Use caching for:

  * pip
  * node_modules

---

## Output

* Only generate the YAML file
* Clean, production-ready
* No explanations
