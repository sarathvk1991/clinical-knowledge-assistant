You are a senior frontend engineer specializing in React, TypeScript, and testing.

I have a React + Vite + TypeScript frontend for a GenAI RAG application.

---

## Project Context

Components:

1. DocumentUpload

   * Uploads PDF/TXT files
   * Has "Load Sample Data" button
   * Uses API to upload

2. DocumentList

   * Displays uploaded documents
   * Supports delete

3. QueryInput

   * Accepts user question
   * Triggers API call

4. ResponseDisplay

   * Shows:

     * answer
     * confidence
     * sources
     * disclaimer

5. StatusBar

   * Shows backend health status

---

## Requirements

Set up **frontend testing using:**

* Vitest
* React Testing Library

---

## Tasks

### 1. Install Dependencies

Add required dev dependencies:

* vitest
* @testing-library/react
* @testing-library/jest-dom
* jsdom

---

### 2. Configure Vitest

Create:

* vitest.config.ts

Requirements:

* environment: "jsdom"
* enable globals
* setup file support

---

### 3. Setup File

Create:

* src/test/setup.ts

Include:

* import "@testing-library/jest-dom"

---

### 4. Update package.json

Add script:
"test": "vitest run"

---

### 5. Write Test Files

Create meaningful tests (not trivial):

---

#### DocumentUpload.test.tsx

* renders upload button
* clicking "Load Sample Data" triggers fetch (mocked)
* shows success message after upload

---

#### QueryInput.test.tsx

* input accepts text
* submit triggers callback/API
* empty input should not submit

---

#### ResponseDisplay.test.tsx

* renders answer text
* renders confidence score
* renders sources list
* renders disclaimer

---

### 6. Mocking Rules

* Mock API calls (no real backend)
* Use vi.fn() for mocks
* Avoid network calls

---

### 7. Output Requirements

Generate:

1. Installation commands
2. vitest.config.ts
3. setup.ts
4. package.json scripts update
5. 3 test files (clean, production-quality)

---

## Quality Expectations

* Clean, readable tests
* No unnecessary complexity
* Realistic assertions
* Ready to run immediately

---

Output everything clearly separated by file.

Do NOT include explanations.
