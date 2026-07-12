import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FilmDetail } from "./film-detail";
import type { FilmSource } from "@/lib/api";

const mocks = vi.hoisted(() => ({
  source: null as FilmSource | null,
  loading: false,
}));

vi.mock("@/lib/use-film-source", () => ({
  useFilmSource: () => ({
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
  importFile: () => Promise.resolve({}),
  listManualItems: () => Promise.resolve([]),
  addManualItem: () => Promise.resolve({}),
  deleteManualItem: () => Promise.resolve(),
}));

const FRESH: FilmSource = {
  state: "fresh",
  synced_at: "2026-07-05T09:00:00Z",
  detail: null,
  provider: "trakt",
  mode: "api",
  summary: {
    movies_watched: 84,
    shows_watched: 12,
    episodes_watched: 410,
    hours: 512,
    top_movies: [{ title: "Inception", year: 2010, plays: 3 }],
    top_shows: [{ title: "Breaking Bad", episodes_watched: 62 }],
    recently_watched: [
      { title: "Arrival", media_type: "movie", watched_at: "2026-07-01T20:00:00Z" },
    ],
    last_synced_at: "2026-07-05T09:00:00Z",
  },
};

describe("FilmDetail", () => {
  beforeEach(() => {
    mocks.loading = false;
    mocks.source = null;
  });

  it("muestra los datos reales cuando la fuente está conectada", () => {
    mocks.source = FRESH;
    render(<FilmDetail />);
    expect(screen.getByRole("heading", { name: "Cine y TV" })).toBeInTheDocument();
    expect(screen.getByText("Inception")).toBeInTheDocument();
    expect(screen.getByText("Breaking Bad")).toBeInTheDocument();
    expect(screen.getByText("horas vistas")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /descargar contexto/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /cambiar de fuente/i }),
    ).toBeInTheDocument();
  });

  it("una fuente de import (Letterboxd) muestra su modo sin refrescar", () => {
    mocks.source = { ...FRESH, provider: "letterboxd", mode: "import" };
    render(<FilmDetail />);
    expect(screen.getByText("Letterboxd")).toBeInTheDocument();
    expect(screen.getByText(/import · manual/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /refrescar/i })).toBeNull();
  });

  it("ofrece el selector de proveedores cuando no hay fuente", () => {
    mocks.source = {
      state: "never",
      synced_at: null,
      detail: null,
      provider: null,
      mode: null,
      summary: null,
    };
    render(<FilmDetail />);
    expect(screen.getByText(/conecta tu cine y series/i)).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /trakt/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /letterboxd/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /imdb/i })).toBeInTheDocument();
    // TMDB aún no es conectable: aparece deshabilitado como "pronto".
    expect(screen.getByRole("radio", { name: /tmdb/i })).toBeDisabled();
    expect(screen.getByLabelText(/tu usuario de trakt/i)).toBeInTheDocument();
  });

  it("guía cuando el perfil de Trakt es privado", () => {
    mocks.source = {
      state: "private",
      synced_at: null,
      detail: "Tu perfil de Trakt es privado o el usuario no existe",
      provider: "trakt",
      mode: "api",
      summary: null,
    };
    render(<FilmDetail />);
    expect(
      screen.getByText(/tu perfil de trakt es privado/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/tu usuario de trakt/i)).toBeInTheDocument();
  });

  it("muestra el estado sincronizando", () => {
    mocks.source = {
      state: "syncing",
      synced_at: null,
      detail: null,
      provider: "trakt",
      mode: "api",
      summary: null,
    };
    render(<FilmDetail />);
    expect(screen.getByText(/sincronizando lo que has visto/i)).toBeInTheDocument();
  });
});
