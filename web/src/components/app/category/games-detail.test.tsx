import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { GamesDetail } from "./games-detail";
import type { GamesSource } from "@/lib/api";

const mocks = vi.hoisted(() => ({
  source: null as GamesSource | null,
  loading: false,
}));

vi.mock("@/lib/use-games-source", () => ({
  useGamesSource: () => ({
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
  refreshSteam: () => Promise.resolve(),
  getSteamLoginUrl: () => Promise.resolve("https://steamcommunity.com/openid/login"),
  listManualItems: () => Promise.resolve([]),
  addManualItem: () => Promise.resolve({}),
  deleteManualItem: () => Promise.resolve(),
}));

const FRESH: GamesSource = {
  state: "fresh",
  synced_at: "2026-07-03T12:00:00Z",
  detail: null,
  provider: "steam",
  mode: "api",
  persona_name: "Jugador",
  summary: {
    games: 312,
    hours: 1840,
    wishlisted: 47,
    avg_completion_pct: 38,
    top_by_hours: [
      {
        title: "Stardew Valley",
        hours: 412,
        completion_pct: 91,
        genres: ["Simulación", "Indie"],
      },
    ],
    recently_played: [{ title: "Balatro", hours_2weeks: 6.2 }],
    top_genres: [{ name: "Simulación", games: 1 }],
    persona_name: "Jugador",
    last_synced_at: "2026-07-03T12:00:00Z",
  },
};

describe("GamesDetail", () => {
  beforeEach(() => {
    mocks.loading = false;
    mocks.source = null;
  });

  it("muestra los datos reales cuando la fuente está conectada", () => {
    mocks.source = FRESH;
    render(<GamesDetail />);
    expect(screen.getByRole("heading", { name: "Juegos" })).toBeInTheDocument();
    expect(screen.getByText("Stardew Valley")).toBeInTheDocument();
    expect(screen.getByText("Jugado recientemente")).toBeInTheDocument();
    // Géneros enriquecidos (D55): en el sub del top y como chips agregados.
    expect(screen.getByText(/Simulación · Indie/)).toBeInTheDocument();
    expect(screen.getByText("Géneros dominantes")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /descargar contexto/i }),
    ).toBeInTheDocument();
  });

  it("ofrece conectar Steam cuando está apagada", () => {
    mocks.source = {
      state: "never",
      synced_at: null,
      detail: null,
      provider: null,
      mode: null,
      persona_name: null,
      summary: null,
    };
    render(<GamesDetail />);
    expect(screen.getByText(/esta categoría está apagada/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /conectar steam/i }),
    ).toBeInTheDocument();
    // Estado del catálogo de proveedores de Juegos (D62).
    expect(screen.getByText(/más proveedores en camino/i)).toBeInTheDocument();
    // Entradas a mano también sin proveedor conectado (D51).
    expect(screen.getByText("Añadido a mano")).toBeInTheDocument();
  });

  it("muestra la sincronización mientras corre el primer refresco", () => {
    mocks.source = {
      state: "syncing",
      synced_at: null,
      detail: null,
      provider: "steam",
      mode: "api",
      persona_name: null,
      summary: null,
    };
    render(<GamesDetail />);
    expect(
      screen.getByText(/sincronizando tu biblioteca/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/se actualizará sola/i)).toBeInTheDocument();
  });

  it("muestra sincronización al volver de conectar aunque el estado siga en never", () => {
    // /steam/return deja esta marca; el primer refresco arranca en segundo
    // plano, así que el estado puede seguir en "never" al primer fetch.
    sessionStorage.setItem("ethos_just_connected_games", "1");
    mocks.source = {
      state: "never",
      synced_at: null,
      detail: null,
      provider: null,
      mode: null,
      persona_name: null,
      summary: null,
    };
    render(<GamesDetail />);
    expect(
      screen.getByText(/sincronizando tu biblioteca/i),
    ).toBeInTheDocument();
    expect(sessionStorage.getItem("ethos_just_connected_games")).toBeNull();
  });

  it("guía cuando el perfil de Steam es privado", () => {
    mocks.source = {
      state: "private",
      synced_at: null,
      detail: "El perfil de Steam es privado",
      provider: "steam",
      mode: "api",
      persona_name: "Jugador",
      summary: null,
    };
    render(<GamesDetail />);
    expect(
      screen.getAllByText(/perfil de steam es privado/i).length,
    ).toBeGreaterThan(0);
  });
});
