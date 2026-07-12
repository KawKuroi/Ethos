import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ConnectAi } from "./connect";

const mocks = vi.hoisted(() => ({
  issueMcpToken: vi.fn(),
  mcpEndpoint: vi.fn(() => "https://api.test/mcp/"),
  getMcpStatus: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  issueMcpToken: mocks.issueMcpToken,
  mcpEndpoint: mocks.mcpEndpoint,
  getMcpStatus: mocks.getMcpStatus,
}));

describe("ConnectAi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.mcpEndpoint.mockReturnValue("https://api.test/mcp/");
    mocks.issueMcpToken.mockResolvedValue({
      token: "eth_live_secreto123",
      endpoint: "https://api.test/mcp/",
    });
    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: false,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
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

    mocks.getMcpStatus.mockResolvedValue({
      oauth_connected: true,
      token_issued: false,
      endpoint: "https://api.test/mcp/",
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
    });
    fireEvent.click(boton);
    expect(await screen.findByText("Tu IA está conectada")).toBeInTheDocument();
    expect(mocks.getMcpStatus).toHaveBeenCalledTimes(2);
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
