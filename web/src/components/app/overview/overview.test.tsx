import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Overview } from "./overview";

const mcp = vi.hoisted(() => ({
  status: {
    oauth_connected: false,
    token_issued: false,
    endpoint: "https://api.test/mcp/",
  } as { oauth_connected: boolean; token_issued: boolean; endpoint: string } | null,
}));

vi.mock("@/lib/use-mcp-status", async (importOriginal) => {
  const original = await importOriginal<typeof import("@/lib/use-mcp-status")>();
  return {
    isMcpConnected: original.isMcpConnected,
    useMcpStatus: () => ({
      loading: false,
      status: mcp.status,
      error: false,
      reload: () => {},
    }),
  };
});

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
        top_by_hours: [
          { title: "Stardew Valley", hours: 412, completion_pct: 91, genres: [] },
        ],
        recently_played: [{ title: "Balatro", hours_2weeks: 6.2 }],
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
        top_artists: [{ name: "Radiohead", count: 88 }],
        top_tracks: [{ name: "Idioteque — Radiohead", count: 12 }],
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
    source: {
      state: "fresh",
      synced_at: "2026-07-05T09:00:00Z",
      detail: null,
      summary: {
        movies_watched: 84,
        shows_watched: 12,
        episodes_watched: 410,
        hours: 512,
        top_movies: [],
        top_shows: [],
        recently_watched: [],
        last_synced_at: "2026-07-05T09:00:00Z",
      },
    },
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

describe("Overview", () => {
  it("muestra el banner de IA sin conectar", () => {
    render(<Overview />);
    expect(screen.getByText(/tu ia aún no está conectada/i)).toBeInTheDocument();
  });

  it("oculta el banner cuando la IA ya está conectada", () => {
    mcp.status = {
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
    };
    render(<Overview />);
    expect(screen.queryByText(/tu ia aún no está conectada/i)).toBeNull();
    mcp.status = {
      oauth_connected: false,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
    };
  });

  it("muestra el stat band con las cifras reales", () => {
    render(<Overview />);
    expect(screen.getByText(/el gusto en números/i)).toBeInTheDocument();
    expect(screen.getByText("312")).toBeInTheDocument();
    expect(screen.getByText("47")).toBeInTheDocument();
    expect(screen.getByText("38%")).toBeInTheDocument();
  });

  it("muestra las fuentes activas y las apagadas en el panorama", () => {
    render(<Overview />);
    expect(screen.getByText("Panorama · por actividad")).toBeInTheDocument();
    expect(screen.getAllByText("horas jugadas").length).toBeGreaterThan(0);
    expect(screen.getAllByText("escuchas").length).toBeGreaterThan(0);
    expect(screen.getAllByText("horas vistas").length).toBeGreaterThan(0);
    // Anime y Libros aún sin conectar: fila apagada con CTA.
    expect(screen.getByText("Anime y manga")).toBeInTheDocument();
    expect(screen.getByText("Libros")).toBeInTheDocument();
    expect(screen.getAllByText(/conéctala →/i)).toHaveLength(2);
  });

  it("cuenta las fuentes activas en la meta del stat band", () => {
    render(<Overview />);
    expect(
      screen.getByText("3 fuentes activas · Steam · ListenBrainz · Trakt"),
    ).toBeInTheDocument();
  });

  it("muestra la actividad reciente real", () => {
    render(<Overview />);
    expect(screen.getByText("Actividad reciente")).toBeInTheDocument();
    expect(screen.getByText(/jugaste a balatro/i)).toBeInTheDocument();
  });
});
