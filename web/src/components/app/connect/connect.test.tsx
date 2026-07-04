import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ConnectAi } from "./connect";

const mocks = vi.hoisted(() => ({
  issueMcpToken: vi.fn(),
  mcpEndpoint: vi.fn(() => "https://api.test/mcp/"),
}));

vi.mock("@/lib/api", () => ({
  issueMcpToken: mocks.issueMcpToken,
  mcpEndpoint: mocks.mcpEndpoint,
}));

describe("ConnectAi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.mcpEndpoint.mockReturnValue("https://api.test/mcp/");
    mocks.issueMcpToken.mockResolvedValue({
      token: "eth_live_secreto123",
      endpoint: "https://api.test/mcp/",
    });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("muestra el endpoint y genera el token bajo demanda", async () => {
    render(<ConnectAi />);
    expect(screen.getByText("https://api.test/mcp/")).toBeInTheDocument();
    expect(screen.getByText("Abre tu cliente de IA")).toBeInTheDocument();

    // El token no se muestra hasta generarlo (POST rota, no se puede recuperar).
    expect(screen.queryByText(/eth_live_/)).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /generar token/i }));
    await waitFor(() =>
      expect(screen.getByText("eth_live_secreto123")).toBeInTheDocument(),
    );
  });

  it("responde a una consulta y muestra el panel técnico", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    fireEvent.click(
      screen.getByRole("button", { name: /mis juegos con más horas/i }),
    );
    // La tool aparece de inmediato; tras el typing efímero llega el 200 OK.
    expect(screen.getByText("games.top_by_hours")).toBeInTheDocument();
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getAllByText(/stardew valley/i).length).toBeGreaterThan(0);
    expect(screen.getByText("200 OK")).toBeInTheDocument();
  });

  it("una consulta sin categoría activa cae en profile.search", () => {
    vi.useFakeTimers();
    render(<ConnectAi />);
    const input = screen.getByLabelText(/escribe tu pregunta/i);
    fireEvent.change(input, { target: { value: "¿qué escuché?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText("profile.search")).toBeInTheDocument();
  });
});
