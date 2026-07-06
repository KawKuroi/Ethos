import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { BooksDetail } from "./books-detail";
import type { BooksSource } from "@/lib/api";

const mocks = vi.hoisted(() => ({
  source: null as BooksSource | null,
  loading: false,
}));

vi.mock("@/lib/use-books-source", () => ({
  useBooksSource: () => ({
    loading: mocks.loading,
    error: false,
    reload: () => {},
    silentReload: () => {},
    source: mocks.source,
  }),
}));

vi.mock("@/lib/api", () => ({
  getContextText: () => Promise.resolve("{}"),
  downloadContext: () => Promise.resolve(),
  importFile: () =>
    Promise.resolve({
      provider: "goodreads",
      category: "books",
      status: "imported",
      items: 4,
    }),
  listManualItems: () => Promise.resolve([]),
  addManualItem: () => Promise.resolve({}),
  deleteManualItem: () => Promise.resolve(),
  ApiError: class ApiError extends Error {},
}));

const FRESH: BooksSource = {
  state: "fresh",
  synced_at: "2026-07-05T09:00:00Z",
  detail: null,
  summary: {
    books_read: 58,
    pages_read: 19204,
    currently_reading: [{ title: "Project Hail Mary", author: "Andy Weir" }],
    wishlisted: 12,
    top_authors: [{ name: "Ursula K. Le Guin", books: 6 }],
    recent_reads: [
      {
        title: "El nombre del viento",
        author: "Patrick Rothfuss",
        finished_at: "2026-06-20T00:00:00Z",
        rating: 100,
      },
    ],
    last_synced_at: "2026-07-05T09:00:00Z",
  },
};

describe("BooksDetail", () => {
  beforeEach(() => {
    mocks.loading = false;
    mocks.source = null;
  });

  it("muestra los datos reales cuando hay import", () => {
    mocks.source = FRESH;
    render(<BooksDetail />);
    expect(screen.getByRole("heading", { name: "Libros" })).toBeInTheDocument();
    expect(screen.getByText("Project Hail Mary")).toBeInTheDocument();
    expect(screen.getByText("Ursula K. Le Guin")).toBeInTheDocument();
    expect(screen.getByText("libros leídos")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /volver a importar/i }),
    ).toBeInTheDocument();
  });

  it("ofrece subir el export cuando no hay datos", () => {
    mocks.source = { state: "never", synced_at: null, detail: null, summary: null };
    render(<BooksDetail />);
    expect(screen.getByText(/sube tus libros/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /subir export/i }),
    ).toBeInTheDocument();
    // La guía de Goodreads acompaña al panel de import.
    expect(
      screen.getByLabelText(/cómo conseguir tu export de goodreads/i),
    ).toBeInTheDocument();
  });
});
