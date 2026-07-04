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

describe("Sources", () => {
  it("muestra el resumen y los grupos", () => {
    render(<Sources />);
    expect(screen.getByText("activas")).toBeInTheDocument();
    expect(screen.getByText("en desarrollo")).toBeInTheDocument();
    expect(screen.getByText("Activas")).toBeInTheDocument();
  });

  it("lista Juegos en Activas con enlace al detalle", () => {
    render(<Sources />);
    const link = screen.getByRole("link", { name: /juegos/i });
    expect(link).toHaveAttribute("href", "/app/categoria/games");
  });

  it("lista las cuatro categorías en desarrollo", () => {
    render(<Sources />);
    for (const name of ["Música", "Cine y TV", "Anime y manga", "Libros"]) {
      expect(
        screen.getByRole("link", { name: new RegExp(name, "i") }),
      ).toBeInTheDocument();
    }
  });
});
