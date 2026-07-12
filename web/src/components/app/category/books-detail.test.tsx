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
  refreshSource: () => Promise.resolve(),
  connectSource: () => Promise.resolve(),
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
  provider: "goodreads",
  mode: "import",
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
    mean_rating: 82,
    rated_count: 41,
    rereads: 3,
    books_this_year: 14,
    longest_book: { title: "La historia interminable", pages: 496 },
    avg_pages: 331,
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
    expect(screen.getByText("Goodreads")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /actualizar o cambiar fuente/i }),
    ).toBeInTheDocument();
    // Un import no refresca por API.
    expect(screen.queryByRole("button", { name: /^refrescar$/i })).toBeNull();
  });

  it("celdas de nota media, año en curso y relecturas, y récords de lectura", () => {
    mocks.source = FRESH;
    render(<BooksDetail />);
    // 82/100 → 4,1 ★.
    expect(screen.getByText("4,1 ★")).toBeInTheDocument();
    expect(screen.getByText("este año")).toBeInTheDocument();
    expect(screen.getByText("relecturas")).toBeInTheDocument();
    expect(screen.getByText("La historia interminable")).toBeInTheDocument();
    expect(screen.getByText(/tu libro más largo · 496 páginas/i)).toBeInTheDocument();
  });

  it("sin páginas ni notas (Open Library) las celdas caen a las básicas", () => {
    mocks.source = {
      ...FRESH,
      provider: "openlibrary",
      summary: {
        ...FRESH.summary!,
        pages_read: 0,
        mean_rating: null,
        rated_count: 0,
        rereads: 0,
        books_this_year: 0,
        longest_book: null,
        avg_pages: null,
      },
    };
    render(<BooksDetail />);
    expect(screen.getByText("leyendo ahora")).toBeInTheDocument();
    expect(screen.getByText("por leer")).toBeInTheDocument();
    expect(screen.queryByText("nota media")).toBeNull();
    expect(screen.queryByText(/récords de lectura/i)).toBeNull();
  });

  it("una fuente API (Hardcover) muestra su modo y ofrece refrescar", () => {
    mocks.source = { ...FRESH, provider: "hardcover", mode: "api" };
    render(<BooksDetail />);
    expect(screen.getByText("Hardcover")).toBeInTheDocument();
    expect(screen.getByText(/api · en vivo/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /refrescar/i }),
    ).toBeInTheDocument();
  });

  it("ofrece el selector de proveedores cuando no hay datos", () => {
    mocks.source = {
      state: "never",
      synced_at: null,
      detail: null,
      provider: null,
      mode: null,
      summary: null,
    };
    render(<BooksDetail />);
    expect(screen.getByText(/conecta tus libros/i)).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /goodreads/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /storygraph/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /hardcover/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /open library/i })).toBeInTheDocument();
    // Goodreads es el proveedor por defecto: guía + botón de subida.
    expect(
      screen.getByLabelText(/cómo conectar goodreads/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /subir export/i }),
    ).toBeInTheDocument();
    // Entradas a mano también sin proveedor conectado (D51).
    expect(screen.getByText("Añadido a mano")).toBeInTheDocument();
  });

  it("muestra el estado sincronizando de una fuente API", () => {
    mocks.source = {
      state: "syncing",
      synced_at: null,
      detail: null,
      provider: "openlibrary",
      mode: "api",
      summary: null,
    };
    render(<BooksDetail />);
    expect(screen.getByText(/sincronizando tus libros/i)).toBeInTheDocument();
  });
});
