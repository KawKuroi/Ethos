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
    mean_rating: null,
    rated_count: 0,
    rating_buckets: [],
    top_rated: [],
    rewatched_count: 0,
    top_genres: [],
    favorite_decade: 2010,
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

  it("con Trakt las celdas son de volumen y la década favorita", () => {
    mocks.source = FRESH;
    render(<FilmDetail />);
    expect(screen.getByText("películas")).toBeInTheDocument();
    expect(screen.getByText("episodios")).toBeInTheDocument();
    expect(screen.getByText("los 2010")).toBeInTheDocument();
    // Sin notas no hay top puntuadas ni distribución.
    expect(screen.queryByText(/mejor puntuadas/i)).toBeNull();
    expect(screen.queryByText(/cómo puntúas/i)).toBeNull();
  });

  it("con notas (Letterboxd) el hero es la nota media y aparecen sus secciones", () => {
    mocks.source = {
      ...FRESH,
      provider: "letterboxd",
      mode: "import",
      summary: {
        ...FRESH.summary!,
        hours: 0,
        shows_watched: 0,
        episodes_watched: 0,
        top_shows: [],
        mean_rating: 78,
        rated_count: 40,
        rating_buckets: [
          { stars: 1, count: 1 },
          { stars: 2, count: 3 },
          { stars: 3, count: 8 },
          { stars: 4, count: 18 },
          { stars: 5, count: 10 },
        ],
        top_rated: [
          { title: "Whiplash", year: 2014, media_type: "movie", rating: 100 },
        ],
        rewatched_count: 6,
        top_genres: [{ name: "Drama", works: 21 }],
      },
    };
    render(<FilmDetail />);
    expect(screen.getByText("tu nota media")).toBeInTheDocument();
    expect(screen.getByText("3,9 ★")).toBeInTheDocument();
    expect(screen.getByText(/mejor puntuadas/i)).toBeInTheDocument();
    expect(screen.getByText("Whiplash")).toBeInTheDocument();
    expect(screen.getByText(/cómo puntúas · 40 notas/i)).toBeInTheDocument();
    expect(screen.getByText(/drama · 21/i)).toBeInTheDocument();
    expect(screen.getByText("repetidas")).toBeInTheDocument();
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
    // Entradas a mano también sin proveedor conectado (D51).
    expect(screen.getByText("Añadido a mano")).toBeInTheDocument();
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
