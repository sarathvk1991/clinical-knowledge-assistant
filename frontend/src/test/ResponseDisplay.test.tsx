import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
import ResponseDisplay from "../components/ResponseDisplay";
import type { QueryResponse } from "../types";

const baseResponse: QueryResponse = {
  answer: "Lisinopril is the first-line treatment for hypertension.",
  sources: [
    {
      document_name: "hypertension_guidelines.pdf",
      chunk_index: 2,
      text_excerpt: "ACE inhibitors such as lisinopril are recommended as first-line agents.",
      similarity_score: 0.923,
    },
    {
      document_name: "cardiology_handbook.txt",
      chunk_index: 7,
      text_excerpt: "Thiazide diuretics are an alternative first-line option.",
      similarity_score: 0.871,
    },
  ],
  confidence: {
    score: 0.88,
    level: "high",
    reasoning: "High confidence: 5 chunk(s) retrieved, avg similarity 0.89.",
  },
  disclaimer: "This information is for educational purposes only and does not constitute medical advice.",
};

describe("ResponseDisplay", () => {
  it("renders nothing when response is null and not loading", () => {
    const { container } = render(<ResponseDisplay response={null} loading={false} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders loading indicator while loading", () => {
    render(<ResponseDisplay response={null} loading={true} />);
    expect(screen.getByText(/analyzing clinical documents/i)).toBeInTheDocument();
  });

  it("renders the answer text", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    expect(screen.getByText(baseResponse.answer)).toBeInTheDocument();
  });

  it("renders confidence badge with correct level", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("renders confidence score and reasoning", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    // 0.88 * 100 = 88.0%
    expect(screen.getByText(/88\.0%/)).toBeInTheDocument();
    expect(screen.getByText(/High confidence/)).toBeInTheDocument();
  });

  it("renders all source cards with document names and similarity scores", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    expect(screen.getByText("hypertension_guidelines.pdf")).toBeInTheDocument();
    expect(screen.getByText("cardiology_handbook.txt")).toBeInTheDocument();
    expect(screen.getByText(/92\.3%/)).toBeInTheDocument();
    expect(screen.getByText(/87\.1%/)).toBeInTheDocument();
  });

  it("renders source text excerpts", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    expect(screen.getByText(/ACE inhibitors such as lisinopril/)).toBeInTheDocument();
    expect(screen.getByText(/Thiazide diuretics are an alternative/)).toBeInTheDocument();
  });

  it("renders the disclaimer", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    expect(screen.getByText(baseResponse.disclaimer)).toBeInTheDocument();
  });

  it("does not render source section when sources array is empty", () => {
    const noSources: QueryResponse = { ...baseResponse, sources: [] };
    render(<ResponseDisplay response={noSources} loading={false} />);
    expect(screen.queryByText("Sources")).not.toBeInTheDocument();
  });

  it("does not render debug section when debug data is absent", () => {
    render(<ResponseDisplay response={baseResponse} loading={false} />);
    expect(screen.queryByText("Debug Info")).not.toBeInTheDocument();
  });

  it("renders debug section with collapsible panels when debug data is present", async () => {
    const withDebug: QueryResponse = {
      ...baseResponse,
      debug: {
        retrieved_chunks: [
          {
            document_name: "hypertension_guidelines.pdf",
            chunk_index: 0,
            text_excerpt: "Retrieved chunk text.",
            similarity_score: 0.91,
          },
        ],
        reranked_chunks: [],
        final_selected_chunks: [],
      },
    };

    render(<ResponseDisplay response={withDebug} loading={false} />);

    expect(screen.getByText("Debug Info")).toBeInTheDocument();

    // Panel is collapsed by default — expand it
    const panel = screen.getByRole("button", { name: /retrieved chunks/i });
    expect(panel).toBeInTheDocument();
    await userEvent.click(panel);

    expect(screen.getByText("Retrieved chunk text.")).toBeInTheDocument();
  });
});
