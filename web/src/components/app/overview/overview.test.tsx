import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Overview } from "./overview";

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
        top_by_hours: [{ title: "Stardew Valley", hours: 412, completion_pct: 91 }],
        recently_played: [{ title: "Balatro", hours_2weeks: 6.2 }],
        persona_name: "Jugador",
        last_synced_at: "2026-07-03T12:00:00Z",
      },
    },
  }),
}));

describe("Overview", () => {
  it("muestra el banner de IA sin conectar", () => {
    render(<Overview />);
    expect(screen.getByText(/tu ia aún no está conectada/i)).toBeInTheDocument();
  });

  it("muestra el stat band con las cifras reales", () => {
    render(<Overview />);
    expect(screen.getByText(/el gusto en números/i)).toBeInTheDocument();
    expect(screen.getByText("312")).toBeInTheDocument();
    expect(screen.getByText("47")).toBeInTheDocument();
    expect(screen.getByText("38%")).toBeInTheDocument();
  });

  it("muestra Juegos activa y categorías en desarrollo en el panorama", () => {
    render(<Overview />);
    expect(screen.getByText("Panorama · por actividad")).toBeInTheDocument();
    expect(screen.getAllByText("horas jugadas").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/en desarrollo · próximamente/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Anime y manga")).toBeInTheDocument();
  });

  it("muestra la actividad reciente real", () => {
    render(<Overview />);
    expect(screen.getByText("Actividad reciente")).toBeInTheDocument();
    expect(screen.getByText(/jugaste a balatro/i)).toBeInTheDocument();
  });
});
