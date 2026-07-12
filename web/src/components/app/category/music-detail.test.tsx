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
    distinct_artists_window: 64,
    avg_per_day_window: 16,
    new_artists_window: 9,
    estimated_hours_window: 28,
    peak_weekday: { weekday: 6, count: 120 },
    top_release: { name: "Kid A — Radiohead", count: 35 },
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

  it("las celdas cuentan ritmo, variedad y descubrimiento de la ventana", () => {
    mocks.source = FRESH;
    render(<MusicDetail />);
    // Tiempo de escucha estimado, marcado como aproximación.
    expect(screen.getByText("≈ 28 h")).toBeInTheDocument();
    expect(screen.getByText("artistas distintos")).toBeInTheDocument();
    expect(screen.getByText("artistas nuevos")).toBeInTheDocument();
    // El álbum más escuchado de la ventana tiene su propia sección.
    expect(screen.getByText("Kid A — Radiohead")).toBeInTheDocument();
  });

  it("oculta las celdas sin dato (fuente sin álbum, ventana vacía)", () => {
    mocks.source = {
      ...FRESH,
      summary: {
        ...FRESH.summary!,
        scrobbles_window: 0,
        distinct_artists_window: 0,
        avg_per_day_window: 0,
        new_artists_window: 0,
        estimated_hours_window: 0,
        peak_weekday: null,
        top_release: null,
      },
    };
    render(<MusicDetail />);
    expect(screen.queryByText("tiempo de escucha")).toBeNull();
    expect(screen.queryByText(/álbum de la ventana/i)).toBeNull();
    expect(screen.getByText(/sin escuchas recientes/i)).toBeInTheDocument();
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
