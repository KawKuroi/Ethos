import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { invalidateSourceCache } from "@/lib/use-source";
import { ConnectAi } from "./connect";

const mocks = vi.hoisted(() => ({
  issueMcpToken: vi.fn(),
  mcpEndpoint: vi.fn(() => "https://api.test/mcp/"),
  getMcpStatus: vi.fn(),
  revokeMcpClient: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  issueMcpToken: mocks.issueMcpToken,
  mcpEndpoint: mocks.mcpEndpoint,
  getMcpStatus: mocks.getMcpStatus,
  revokeMcpClient: mocks.revokeMcpClient,
}));

const NO_USAGE = { total_calls: 0, last_called_at: null, top_tools: [] };

describe("ConnectAi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // El estado del MCP se cachea entre montajes (useSource): cada test
    // parte de una caché limpia para que su mock mande.
    invalidateSourceCache();
    mocks.mcpEndpoint.mockReturnValue("https://api.test/mcp/");
    mocks.issueMcpToken.mockResolvedValue({
      token: "eth_live_secreto123",
      endpoint: "https://api.test/mcp/",
    });
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: false,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
      clients: [],
      usage: NO_USAGE,
    });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("muestra el endpoint y genera el token bajo demanda", async () => {
    render(<ConnectAi />);
    expect(screen.getByText("https://api.test/mcp/")).toBeInTheDocument();

    // El token no se muestra hasta generarlo (POST rota, no se puede recuperar).
    expect(screen.queryByText(/eth_live_/)).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /generar token/i }));
    await waitFor(() =>
      expect(screen.getByText("eth_live_secreto123")).toBeInTheDocument(),
    );
  });

  it("muestra el estado real: desconectada sin OAuth, conectada con OAuth", async () => {
    const { unmount } = render(<ConnectAi />);
    expect(
      await screen.findByText("Tu IA aún no está conectada"),
    ).toBeInTheDocument();
    unmount();
    invalidateSourceCache();

    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
      clients: [],
      usage: NO_USAGE,
    });
    render(<ConnectAi />);
    expect(await screen.findByText("Tu IA está conectada")).toBeInTheDocument();
  });

  it("«Comprobar conexión» vuelve a consultar el estado", async () => {
    render(<ConnectAi />);
    const boton = await screen.findByRole("button", {
      name: /comprobar conexión/i,
    });
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
      clients: [],
      usage: NO_USAGE,
    });
    fireEvent.click(boton);
    expect(await screen.findByText("Tu IA está conectada")).toBeInTheDocument();
    expect(mocks.getMcpStatus).toHaveBeenCalledTimes(2);
  });

  it("conectada: muestra la actividad y pliega la guía de conexión", async () => {
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
      clients: [{ name: "Claude", connected_at: "2026-07-10T00:00:00Z" }],
      usage: {
        total_calls: 12,
        last_called_at: "2026-07-11T00:00:00Z",
        top_tools: [{ tool: "games_summary", calls: 8 }],
      },
    });
    render(<ConnectAi />);

    expect(await screen.findByText("Tu IA está conectada")).toBeInTheDocument();
    expect(screen.getByText(/autorizada para claude/i)).toBeInTheDocument();
    expect(screen.getByText("consultas atendidas")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("×8")).toBeInTheDocument();
    // La guía queda plegada como "Conectar otro cliente".
    expect(screen.getByText("Conectar otro cliente")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /comprobar conexión/i }),
    ).toBeNull();
    expect(
      screen.getByRole("button", { name: /actualizar estado/i }),
    ).toBeInTheDocument();
  });

  it("revoca un cliente desde su chip y recarga el estado", async () => {
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
      clients: [
        {
          client_id: "eth_client_abc",
          name: "Claude",
          connected_at: "2026-07-10T00:00:00Z",
        },
      ],
      usage: NO_USAGE,
    });
    mocks.revokeMcpClient.mockResolvedValue(undefined);
    render(<ConnectAi />);

    const boton = await screen.findByRole("button", {
      name: /revocar el acceso de claude/i,
    });
    fireEvent.click(boton);

    await waitFor(() =>
      expect(mocks.revokeMcpClient).toHaveBeenCalledWith("eth_client_abc"),
    );
    // Tras revocar se vuelve a consultar el estado (carga inicial + recarga).
    await waitFor(() => expect(mocks.getMcpStatus).toHaveBeenCalledTimes(2));
  });

  it("un cliente sin client_id no ofrece revocación", async () => {
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
      clients: [{ name: "Claude", connected_at: null }],
      usage: NO_USAGE,
    });
    render(<ConnectAi />);
    expect(await screen.findByText("Tu IA está conectada")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /revocar/i })).toBeNull();
  });

  it("conectada sin consultas: invita a hacer la primera", async () => {
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: false,
      token_issued: true,
      endpoint: "https://api.test/mcp/",
      clients: [],
      usage: NO_USAGE,
    });
    render(<ConnectAi />);
    expect(await screen.findByText("Tu IA está conectada")).toBeInTheDocument();
    expect(screen.getByText(/aún no ha hecho consultas/i)).toBeInTheDocument();
    expect(screen.getByText("Token manual")).toBeInTheDocument();
  });

  it("ofrece guías por cliente en pestañas, con Claude por defecto", async () => {
    render(<ConnectAi />);
    expect(
      screen.getByRole("tab", { name: "Claude", selected: true }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/«añadir conector personalizado»/i),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Claude Code" }));
    expect(
      screen.getByText(
        "claude mcp add --transport http ethos https://api.test/mcp/",
      ),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Cursor" }));
    expect(screen.getByText(/"mcpServers"/)).toBeInTheDocument();
    await screen.findByText("Tu IA aún no está conectada");
  });

  it("avisa de que el playground usa datos de ejemplo", () => {
    render(<ConnectAi />);
    expect(screen.getByRole("note")).toHaveTextContent(/datos de ejemplo/i);
    expect(screen.getByRole("note")).toHaveTextContent(/no consulta tu perfil real/i);
  });

  it("responde a una consulta y muestra el panel técnico", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    fireEvent.click(
      screen.getByRole("button", { name: /mis juegos con más horas/i }),
    );
    // La tool aparece de inmediato; tras el typing efímero llega el 200 OK.
    expect(screen.getByText("games_top_by_hours")).toBeInTheDocument();
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getAllByText(/stardew valley/i).length).toBeGreaterThan(0);
    expect(screen.getByText("200 OK")).toBeInTheDocument();
  });

  it("enruta una consulta de música a music.top_artists", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    const input = screen.getByLabelText(/escribe tu pregunta/i);
    fireEvent.change(input, { target: { value: "¿mis artistas más escuchados?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getAllByText("music_top_artists").length).toBeGreaterThan(1);
  });

  it("enruta una consulta de series a film.top_movies", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    const input = screen.getByLabelText(/escribe tu pregunta/i);
    fireEvent.change(input, { target: { value: "¿qué series vi?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText("film_top_movies")).toBeInTheDocument();
  });

  it("enruta libros y anime a sus tools", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    const input = screen.getByLabelText(/escribe tu pregunta/i);
    fireEvent.change(input, { target: { value: "¿qué libro estoy leyendo?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText("books_currently_reading")).toBeInTheDocument();

    fireEvent.change(input, { target: { value: "¿mi manga favorito?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText("anime_top_rated")).toBeInTheDocument();
  });

  it("una consulta sin categoría reconocible cae en profile.search", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    const input = screen.getByLabelText(/escribe tu pregunta/i);
    fireEvent.change(input, { target: { value: "¿mi comida preferida?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText("profile_search")).toBeInTheDocument();
  });
});
