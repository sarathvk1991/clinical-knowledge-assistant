Enhance query_service to support lightweight conversation memory.

Requirements:

1. Add optional session_id parameter to process_query

2. Maintain an in-memory store:
   SESSION_STORE: Dict[str, List[Dict]]

3. For each request:
   - Fetch history using session_id
   - Pass history into generate_answer

4. After successful response:
   - Append user question and assistant answer to memory

5. Limit memory to last 6 messages (3 interactions)

6. Do NOT update memory on fallback responses or failures

7. Ensure session_id is optional and backward compatible

8. Keep implementation simple (no threading concerns)

Output clean updated query_service.py only