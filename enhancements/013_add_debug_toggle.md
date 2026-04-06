Enhance the frontend React application with a Debug Mode toggle.

Requirements:

1. Add a checkbox or toggle switch labeled "Show Debug Info" in the main query UI.

2. When enabled:
   - Pass a query parameter `debug=true` in the API request to /api/query
   - Example:
     POST /api/query
     body: { question: "...", debug: true }

3. Update ResponseDisplay component:
   - If debug data exists in response:
     - Display sections:
       a. Retrieved Chunks
       b. Reranked Chunks
       c. Final Selected Chunks
       d. Scores (similarity + rerank)

4. Format:
   - Use collapsible panels or sections
   - Display chunk text excerpts, scores, and document names

5. Ensure:
   - Debug UI is hidden when toggle is OFF
   - No breaking changes to existing UI

Goal:
Expose internal RAG pipeline for explainability and demo purposes.