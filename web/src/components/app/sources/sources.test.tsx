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

describe("Sources", () => {
  it("muestra el resumen y los grupos", () => {
    render(<Sources />);
    expect(screen.getByText("activas")).toBeInTheDocument();
    expect(screen.getByText("en desarrollo")).toBeInTheDocument();
    expect(screen.getByText("Activas")).toBeInTheDocument();
  });

  it("lista Juegos y Música en Activas con enlace al detalle", () => {
    render(<Sources />);
    expect(screen.getByRole("link", { name: /juegos/i })).toHaveAttribute(
      "href",
      "/app/categoria/games",
    );
    expect(screen.getByRole("link", { name: /música/i })).toHaveAttribute(
      "href",
      "/app/categoria/music",
    );
  });

  it("lista las tres categorías en desarrollo", () => {
    render(<Sources />);
    for (const name of ["Cine y TV", "Anime y manga", "Libros"]) {
      expect(
        screen.getByRole("link", { name: new RegExp(name, "i") }),
      ).toBeInTheDocument();
    }
  });
});
