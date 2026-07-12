import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AnimeDetail } from "./anime-detail";
import type { AnimeSource } from "@/lib/api";

const mocks = vi.hoisted(() => ({
  source: null as AnimeSource | null,
  loading: false,
}));

vi.mock("@/lib/use-anime-source", () => ({
  useAnimeSource: () => ({
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

const FRESH: AnimeSource = {
  state: "fresh",
  synced_at: "2026-07-05T09:00:00Z",
  detail: null,
  provider: "anilist",
  mode: "api",
  summary: {
    anime_watched: 42,
    manga_read: 7,
    episodes_watched: 980,
    chapters_read: 611,
    mean_score: 84.5,
    top_rated: [
      { title: "Berserk", media_type: "manga", score: 100, progress: 205 },
    ],
    current: [{ title: "One Piece", media_type: "anime", progress: 8 }],
    last_synced_at: "2026-07-05T09:00:00Z",
  },
};

describe("AnimeDetail", () => {
  beforeEach(() => {
    mocks.loading = false;
    mocks.source = null;
  });

  it("muestra los datos reales cuando la fuente está conectada", () => {
    mocks.source = FRESH;
    render(<AnimeDetail />);
    expect(
      screen.getByRole("heading", { name: "Anime y manga" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Berserk")).toBeInTheDocument();
    expect(screen.getByText("One Piece")).toBeInTheDocument();
    expect(screen.getByText("episodios vistos")).toBeInTheDocument();
    expect(screen.getByText("nota media")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /cambiar de fuente/i }),
    ).toBeInTheDocument();
  });

  it("reporta el proveedor real de la fuente (MyAnimeList)", () => {
    mocks.source = { ...FRESH, provider: "mal" };
    render(<AnimeDetail />);
    expect(screen.getByText("MyAnimeList")).toBeInTheDocument();
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
    render(<AnimeDetail />);
    expect(screen.getByText(/conecta tu anime y manga/i)).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /anilist/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /myanimelist/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /kitsu/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/tu usuario de anilist/i)).toBeInTheDocument();
    // Entradas a mano también sin proveedor conectado (D51).
    expect(screen.getByText("Añadido a mano")).toBeInTheDocument();
  });

  it("guía cuando las listas son privadas", () => {
    mocks.source = {
      state: "private",
      synced_at: null,
      detail: "Tu usuario de AniList no existe o sus listas son privadas",
      provider: "anilist",
      mode: "api",
      summary: null,
    };
    render(<AnimeDetail />);
    expect(
      screen.getByText(/no existe o sus listas son privadas/i),
    ).toBeInTheDocument();
  });
});
