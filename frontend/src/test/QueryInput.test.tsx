import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import QueryInput from "../components/QueryInput";

vi.mock("../api/client", () => ({
  submitQuery: vi.fn(),
}));

import { submitQuery } from "../api/client";
const mockSubmitQuery = vi.mocked(submitQuery);

const mockResponse = {
  answer: "Lisinopril is the first-line treatment.",
  sources: [],
  confidence: { score: 0.9, level: "high", reasoning: "Strong match." },
  disclaimer: "For educational use only.",
};

describe("QueryInput", () => {
  const onResponse = vi.fn();
  const onLoading = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the textarea and submit button", () => {
    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    expect(screen.getByPlaceholderText(/enter your clinical question/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /submit query/i })).toBeInTheDocument();
  });

  it("submit button is disabled when input is empty", () => {
    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    expect(screen.getByRole("button", { name: /submit query/i })).toBeDisabled();
  });

  it("submit button enables when user types a question", async () => {
    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    await userEvent.type(screen.getByPlaceholderText(/enter your clinical question/i), "What is metformin?");

    expect(screen.getByRole("button", { name: /submit query/i })).toBeEnabled();
  });

  it("does not call API when submitting empty or whitespace input", async () => {
    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    const textarea = screen.getByPlaceholderText(/enter your clinical question/i);
    await userEvent.type(textarea, "   ");

    // Button should still be disabled — form won't submit
    expect(screen.getByRole("button", { name: /submit query/i })).toBeDisabled();
    expect(mockSubmitQuery).not.toHaveBeenCalled();
  });

  it("calls submitQuery with the question on form submit", async () => {
    mockSubmitQuery.mockResolvedValueOnce(mockResponse);

    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    await userEvent.type(
      screen.getByPlaceholderText(/enter your clinical question/i),
      "What is metformin?"
    );
    await userEvent.click(screen.getByRole("button", { name: /submit query/i }));

    await waitFor(() => {
      expect(mockSubmitQuery).toHaveBeenCalledWith(
        expect.objectContaining({ question: "What is metformin?" })
      );
    });
    expect(onResponse).toHaveBeenCalledWith(mockResponse);
  });

  it("passes debug: true when debug mode is enabled", async () => {
    mockSubmitQuery.mockResolvedValueOnce(mockResponse);

    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    await userEvent.click(screen.getByRole("checkbox", { name: /show debug info/i }));
    await userEvent.type(
      screen.getByPlaceholderText(/enter your clinical question/i),
      "What is metformin?"
    );
    await userEvent.click(screen.getByRole("button", { name: /submit query/i }));

    await waitFor(() => {
      expect(mockSubmitQuery).toHaveBeenCalledWith(
        expect.objectContaining({ debug: true })
      );
    });
  });

  it("shows error message when API call fails", async () => {
    mockSubmitQuery.mockRejectedValueOnce(new Error("Network error"));

    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    await userEvent.type(
      screen.getByPlaceholderText(/enter your clinical question/i),
      "What is metformin?"
    );
    await userEvent.click(screen.getByRole("button", { name: /submit query/i }));

    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
    expect(onResponse).not.toHaveBeenCalled();
  });

  it("calls onLoading(true) then onLoading(false) around the API call", async () => {
    mockSubmitQuery.mockResolvedValueOnce(mockResponse);

    render(<QueryInput onResponse={onResponse} onLoading={onLoading} />);

    await userEvent.type(
      screen.getByPlaceholderText(/enter your clinical question/i),
      "What is metformin?"
    );
    await userEvent.click(screen.getByRole("button", { name: /submit query/i }));

    await waitFor(() => expect(onResponse).toHaveBeenCalled());

    expect(onLoading).toHaveBeenCalledWith(true);
    expect(onLoading).toHaveBeenCalledWith(false);
  });
});
