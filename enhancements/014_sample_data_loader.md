Enhance the frontend with a "Load Sample Medical Data" feature.

Requirements:

1. Add a button:
   "Load Sample Medical Data"

2. On click:
   - Automatically upload a predefined sample document (PDF or text)
   - The file can be stored in frontend public/ folder

3. Show:
   - Loading state during upload
   - Success message: "Sample data loaded successfully"

4. Ensure:
   - This uses existing /api/documents/upload API
   - No backend changes required

5. UX:
   - Disable button while uploading
   - Show error if upload fails

Goal:
Make demo reliable without requiring manual file upload.