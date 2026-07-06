import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Sources } from "./sources";

vi.mock("@/lib/use-games-source", () => ({
  useGamesSource: () => ({
    loading: false,
    error: false,
    reload: () => {},
    source: {
      state: "fresh",
      synced_at: "2026-07-03T12:00:00Z",
      detail: null,
      persona_name: "Jugador",
      summary: {
        games: 312,
        hours: 1840,
        wishlisted: 47,
        avg_completion_pct: 38,
        top_by_hours: [],
        recently_played: [],
        persona_name: "Jugador",
        last_synced_at: "2026-07-03T12:00:00Z",
      },
    },
  }),
}));

vi.mock("@/lib/use-music-source", () => ({
  useMusicSource: () => ({
    loading: false,
    error: false,
    reload: () => {},
    source: {
      state: "fresh",
      synced_at: "2026-07-04T12:00:00Z",
      detail: null,
      summary: {
        scrobbles_total: 5210,
        scrobbles_window: 480,
        window_days: 30,
        top_artists: [],
        top_tracks: [],
        last_listened_at: "2026-07-04T12:00:00Z",
      },
    },
  }),
}));

vi.mock("@/lib/use-film-source", () => ({
  useFilmSource: () => ({
    loading: false,
    error: false,
    reload: () => {},
    source: { state: "never", synced_at: null, detail: null, summary: null },
  }),
}));

vi.mock("@/lib/use-anime-source", () => ({
  useAnimeSource: () => ({
    loading: false,
    error: false,
    reload: () => {},
    source: { state: "never", synced_at: null, detail: null, summary: null },
  }),
}));

vi.mock("@/lib/use-books-source", () => ({
  useBooksSource: () => ({
    loading: false,
    error: false,
    reload: () => {},
    source: { state: "never", synced_at: null, detail: null, summary: null },
  }),
}));

describe("Sources", () => {
  it("muestra el resumen y los grupos", () => {
    render(<Sources />);
    expect(screen.getByText("activas")).toBeInTheDocument();
    expect(screen.getByText("apagadas")).toBeInTheDocument();
    expect(screen.getByText("Activas")).toBeInTheDocument();
    expect(screen.getByText(/apagadas · sin empezar/i)).toBeInTheDocument();
  });

  it("lista Juegos y Música en Activas con enlace al detalle", () => {
    render(<Sources />);
    // "Juegos" (activa, CTA "Abrir") vs "Juegos de mesa" (en desarrollo): se
    // desambigua por el CTA de la tarjeta activa.
    expect(screen.getByRole("link", { name: /juegos.*abrir/i })).toHaveAttribute(
      "href",
      "/app/categoria/games",
    );
    expect(screen.getByRole("link", { name: /música/i })).toHaveAttribute(
      "href",
      "/app/categoria/music",
    );
  });

  it("lista las categorías sin datos como apagadas, con CTA de empezar", () => {
    render(<Sources />);
    for (const [name, slug] of [
      ["Cine y TV", "film"],
      ["Anime y manga", "anime"],
      ["Libros", "books"],
    ]) {
      expect(
        screen.getByRole("link", { name: new RegExp(name, "i") }),
      ).toHaveAttribute("href", `/app/categoria/${slug}`);
    }
    expect(screen.getAllByText("Empezar →")).toHaveLength(3);
  });

  it("cuenta el import de Goodreads como método de Libros", () => {
    render(<Sources />);
    expect(screen.getByText(/goodreads · import/i)).toBeInTheDocument();
  });
});
