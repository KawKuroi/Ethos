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
  refreshSource: () => Promise.resolve(),
  connectSource: () => Promise.resolve(),
  importFile: () => Promise.resolve({}),
}));

const FRESH: MusicSource = {
  state: "fresh",
  synced_at: "2026-07-04T12:00:00Z",
  detail: null,
  provider: "listenbrainz",
  mode: "api",
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
    // Multi-proveedor (D62): se puede cambiar de fuente desde el detalle.
    expect(
      screen.getByRole("button", { name: /cambiar de fuente/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("ListenBrainz")).toBeInTheDocument();
  });

  it("una fuente de import muestra su modo y no ofrece refrescar", () => {
    mocks.source = {
      ...FRESH,
      provider: "spotify",
      mode: "import",
    };
    render(<MusicDetail />);
    expect(screen.getByText("Spotify")).toBeInTheDocument();
    expect(screen.getByText(/import · manual/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /refrescar/i })).toBeNull();
    expect(
      screen.getByRole("button", { name: /actualizar o cambiar fuente/i }),
    ).toBeInTheDocument();
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
    render(<MusicDetail />);
    expect(screen.getByText(/conecta tu música/i)).toBeInTheDocument();
    // Los cuatro proveedores de música están en el selector.
    expect(screen.getByRole("radio", { name: /listenbrainz/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /last\.fm/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /spotify/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /apple music/i })).toBeInTheDocument();
    expect(
      screen.getByLabelText(/tu usuario de listenbrainz/i),
    ).toBeInTheDocument();
  });

  it("muestra el estado sincronizando", () => {
    mocks.source = {
      state: "syncing",
      synced_at: null,
      detail: null,
      provider: "listenbrainz",
      mode: "api",
      summary: null,
    };
    render(<MusicDetail />);
    expect(screen.getByText(/sincronizando tus escuchas/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /actualizar/i }),
    ).toBeInTheDocument();
  });
});
