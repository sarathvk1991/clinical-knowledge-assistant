Enhance the system to support prompt versioning.

Requirements:

1. Add PROMPT_VERSION = "v1.0" in clinical_qa prompt file
2. Add EVALUATION_PROMPT_VERSION = "v1.0" in evaluation prompt file

3. Modify llm_service:
   - include prompt_version in response dict

4. Modify evaluation_service:
   - include prompt_version in evaluation result

5. Modify query_service:
   - include both prompt_version and evaluation_prompt_version in QueryResponse

6. Update QueryResponse model:
   - add prompt_version: Optional[str]
   - add evaluation_prompt_version: Optional[str]

7. Ensure backward compatibility (no breaking changes)

Keep implementation clean and minimal.