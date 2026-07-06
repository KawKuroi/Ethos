import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MusicDetail } from "./music-detail";
import type { MusicSource } from "@/lib/api";

const mocks = vi.hoisted(() => ({
  source: null as MusicSource | null,
  loading: false,
}));

vi.mock("@/lib/use-music-source", () => ({
  useMusicSource: () => ({
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
  refreshListenBrainz: () => Promise.resolve(),
  connectListenBrainz: () => Promise.resolve(),
}));

const FRESH: MusicSource = {
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
};

describe("MusicDetail", () => {
  beforeEach(() => {
    mocks.loading = false;
    mocks.source = null;
  });

  it("muestra los datos reales cuando la fuente está conectada", () => {
    mocks.source = FRESH;
    render(<MusicDetail />);
    expect(screen.getByRole("heading", { name: "Música" })).toBeInTheDocument();
    expect(screen.getByText("Radiohead")).toBeInTheDocument();
    expect(screen.getAllByText(/top artistas/i).length).toBeGreaterThan(0);
    expect(
      screen.getByRole("button", { name: /descargar contexto/i }),
    ).toBeInTheDocument();
  });

  it("ofrece conectar ListenBrainz cuando no hay fuente", () => {
    mocks.source = {
      state: "never",
      synced_at: null,
      detail: null,
      summary: null,
    };
    render(<MusicDetail />);
    expect(screen.getByText(/conecta tu música/i)).toBeInTheDocument();
    expect(
      screen.getByLabelText(/nombre de usuario de listenbrainz/i),
    ).toBeInTheDocument();
  });

  it("muestra el estado sincronizando", () => {
    mocks.source = {
      state: "syncing",
      synced_at: null,
      detail: null,
      summary: null,
    };
    render(<MusicDetail />);
    expect(screen.getByText(/sincronizando tus escuchas/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /actualizar/i }),
    ).toBeInTheDocument();
  });
});
