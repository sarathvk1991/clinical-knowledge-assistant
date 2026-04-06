import { useState, useRef, type DragEvent } from "react";
import { uploadDocument } from "../api/client";

interface Props {
  onUploadComplete: () => void;
}

export default function DocumentUpload({ onUploadComplete }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [sampleLoading, setSampleLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setUploading(true);
    setMessage("");
    try {
      const res = await uploadDocument(file);
      setMessage(res.message);
      onUploadComplete();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSample = async () => {
    setSampleLoading(true);
    setMessage("");
    try {
      const response = await fetch("/sample_medical_guidelines.txt");
      if (!response.ok) throw new Error("Failed to fetch sample file");
      const blob = await response.blob();
      const file = new File([blob], "sample_medical_guidelines.txt", { type: "text/plain" });
      const res = await uploadDocument(file);
      setMessage("Sample data loaded successfully");
      void res;
      onUploadComplete();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Failed to load sample data");
    } finally {
      setSampleLoading(false);
    }
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="upload-section">
      <h2>Upload Document</h2>
      <div
        className={`drop-zone ${dragging ? "dragging" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
        {uploading ? (
          <p>Uploading and processing...</p>
        ) : (
          <p>Drag & drop a PDF or TXT file here, or click to browse</p>
        )}
      </div>
      <button
        type="button"
        className="btn-sample"
        onClick={handleLoadSample}
        disabled={sampleLoading || uploading}
      >
        {sampleLoading ? "Loading..." : "Load Sample Medical Data"}
      </button>
      {message && <p className="upload-message">{message}</p>}
    </div>
  );
}
