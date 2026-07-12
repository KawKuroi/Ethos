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
    never_played: 124,
    hours_2weeks: 11.5,
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

  it("celdas de backlog, completado y concentración en el juego nº 1", () => {
    mocks.source = FRESH;
    render(<GamesDetail />);
    // 124 de 312 sin estrenar → 40%.
    expect(screen.getByText("40%")).toBeInTheDocument();
    expect(screen.getByText("sin estrenar")).toBeInTheDocument();
    expect(screen.getByText("38%")).toBeInTheDocument();
    // 412 de 1840 horas en Stardew Valley → 22%.
    expect(screen.getByText("22%")).toBeInTheDocument();
    expect(screen.getByText("en tu juego nº 1")).toBeInTheDocument();
    // Con 4 celdas ya cubiertas, las últimas 2 semanas quedan fuera.
    expect(screen.queryByText("últimas 2 sem")).toBeNull();
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

  it("no pinta la vista conectada con un resumen parcial a ceros mientras sincroniza", () => {
    // Un backend antiguo podía devolver, a mitad del primer refresco, un
    // resumen construido solo con el perfil (todo a cero): eso no son datos.
    mocks.source = {
      state: "syncing",
      synced_at: null,
      detail: null,
      provider: "steam",
      mode: "api",
      persona_name: "Jugador",
      summary: {
        games: 0,
        hours: 0,
        wishlisted: 0,
        avg_completion_pct: null,
        never_played: 0,
        hours_2weeks: 0,
        top_by_hours: [],
        recently_played: [],
        top_genres: [],
        persona_name: "Jugador",
        last_synced_at: null,
      },
    };
    render(<GamesDetail />);
    expect(screen.getByText(/sincronizando tu biblioteca/i)).toBeInTheDocument();
    expect(screen.queryByText("Operativa")).not.toBeInTheDocument();
  });

  it("muestra el error cuando la sincronización falló", () => {
    mocks.source = {
      state: "error",
      synced_at: null,
      detail: "Steam respondió 500 al pedir la biblioteca",
      provider: "steam",
      mode: "api",
      persona_name: null,
      summary: null,
    };
    render(<GamesDetail />);
    expect(
      screen.getByText(/no se pudo sincronizar con steam/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/steam respondió 500 al pedir la biblioteca/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /conectar steam/i }),
    ).toBeInTheDocument();
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
