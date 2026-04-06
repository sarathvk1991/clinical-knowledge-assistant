import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import DocumentUpload from "../components/DocumentUpload";

// Mock the API client
vi.mock("../api/client", () => ({
  uploadDocument: vi.fn(),
}));

import { uploadDocument } from "../api/client";
const mockUploadDocument = vi.mocked(uploadDocument);

// Helper: create a minimal File object
function makeFile(name = "test.txt", type = "text/plain") {
  return new File(["content"], name, { type });
}

describe("DocumentUpload", () => {
  const onUploadComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the drop zone and sample data button", () => {
    render(<DocumentUpload onUploadComplete={onUploadComplete} />);

    expect(screen.getByText(/drag & drop/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /load sample medical data/i })).toBeInTheDocument();
  });

  it("shows success message after uploading a file", async () => {
    mockUploadDocument.mockResolvedValueOnce({
      document_id: "abc",
      document_name: "test.txt",
      chunk_count: 3,
      message: "Document uploaded successfully",
    });

    render(<DocumentUpload onUploadComplete={onUploadComplete} />);

    // Use fireEvent.change to avoid the drop-zone onClick → input.click() recursion in happy-dom
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [makeFile()] } });

    await waitFor(() => {
      expect(screen.getByText("Document uploaded successfully")).toBeInTheDocument();
    });
    expect(onUploadComplete).toHaveBeenCalledOnce();
  });

  it("shows error message when upload fails", async () => {
    mockUploadDocument.mockRejectedValueOnce(new Error("Upload failed"));

    render(<DocumentUpload onUploadComplete={onUploadComplete} />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [makeFile()] } });

    await waitFor(() => {
      expect(screen.getByText("Upload failed")).toBeInTheDocument();
    });
    expect(onUploadComplete).not.toHaveBeenCalled();
  });

  it("clicking Load Sample Medical Data fetches and uploads the sample file", async () => {
    const sampleBlob = new Blob(["sample content"], { type: "text/plain" });
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      blob: () => Promise.resolve(sampleBlob),
    } as unknown as Response);

    mockUploadDocument.mockResolvedValueOnce({
      document_id: "sample-id",
      document_name: "sample_medical_guidelines.txt",
      chunk_count: 10,
      message: "Sample data loaded successfully",
    });

    render(<DocumentUpload onUploadComplete={onUploadComplete} />);

    const btn = screen.getByRole("button", { name: /load sample medical data/i });
    await userEvent.click(btn);

    await waitFor(() => {
      expect(screen.getByText("Sample data loaded successfully")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith("/sample_medical_guidelines.txt");
    expect(mockUploadDocument).toHaveBeenCalledOnce();
    expect(onUploadComplete).toHaveBeenCalledOnce();
  });

  it("disables Load Sample button while uploading", async () => {
    // Never resolves — simulates in-flight request
    global.fetch = vi.fn().mockReturnValueOnce(new Promise(() => {}));

    render(<DocumentUpload onUploadComplete={onUploadComplete} />);

    const btn = screen.getByRole("button", { name: /load sample medical data/i });
    await userEvent.click(btn);

    expect(btn).toBeDisabled();
    expect(btn).toHaveTextContent("Loading...");
  });

  it("shows error when sample fetch fails", async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
    } as unknown as Response);

    render(<DocumentUpload onUploadComplete={onUploadComplete} />);

    const btn = screen.getByRole("button", { name: /load sample medical data/i });
    await userEvent.click(btn);

    await waitFor(() => {
      expect(screen.getByText("Failed to fetch sample file")).toBeInTheDocument();
    });
    expect(onUploadComplete).not.toHaveBeenCalled();
  });
});
