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
        top_genres: [],
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
    // "Juegos" activa: se desambigua por el CTA "Abrir" de la tarjeta activa.
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

  it("señala que las categorías apagadas tienen varios proveedores", () => {
    render(<Sources />);
    // Libros (apagada) ofrece 4 proveedores (Goodreads, StoryGraph, Hardcover,
    // Open Library); la tarjeta lo anuncia sin abrir el detalle.
    expect(screen.getAllByText(/4 proveedores disponibles/i).length).toBeGreaterThan(0);
    const meta = screen
      .getAllByTitle(/proveedores:/i)
      .find((node) => node.title.includes("Goodreads"));
    expect(meta).toBeDefined();
  });

  it("marca en las activas cuántos proveedores alternativos hay", () => {
    render(<Sources />);
    // Juegos activa con Steam: el catálogo tiene 3 proveedores → "+2".
    expect(
      screen.getByTitle(/3 proveedores disponibles: Steam, Xbox, PlayStation/i),
    ).toHaveTextContent("+2");
  });
});
