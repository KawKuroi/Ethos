import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ContextDownloadModal } from "./context-modal";

const mocks = vi.hoisted(() => ({
  contextText: "{}",
}));

vi.mock("@/lib/api", () => ({
  getContextText: () => Promise.resolve(mocks.contextText),
  downloadContext: () => Promise.resolve(),
}));

function contextWith(history: object): string {
  return JSON.stringify({ namespace: "music.*", history }, null, 2);
}

describe("ContextDownloadModal", () => {
  it("muestra el uso del límite cuando el historial está completo", async () => {
    mocks.contextText = contextWith({
      limit: 1000,
      total: 320,
      included: 320,
      usage_pct: 32,
      truncated: false,
      entries: [],
    });
    render(<ContextDownloadModal slug="music" onClose={() => {}} />);

    expect(
      await screen.findByText(/historial completo: 320 entradas · 32 % del límite/i),
    ).toBeInTheDocument();
  });

  it("avisa cuando el historial alcanzó el límite", async () => {
    mocks.contextText = contextWith({
      limit: 1000,
      total: 2431,
      included: 1000,
      usage_pct: 100,
      truncated: true,
      entries: [],
    });
    render(<ContextDownloadModal slug="music" onClose={() => {}} />);

    expect(
      await screen.findByText(
        /límite alcanzado: el historial incluye las 1000 entradas más recientes de 2431/i,
      ),
    ).toBeInTheDocument();
  });

  it("no muestra el indicador si el contexto no trae historial", async () => {
    mocks.contextText = JSON.stringify({ namespace: "music.*" });
    render(<ContextDownloadModal slug="music" onClose={() => {}} />);

    expect(await screen.findByText(/"music\.\*"/)).toBeInTheDocument();
    expect(screen.queryByText(/límite/i)).not.toBeInTheDocument();
  });
});
