import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ConnectAi } from "./connect";

describe("ConnectAi", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("muestra el endpoint, el token y los tres pasos", () => {
    render(<ConnectAi />);
    expect(screen.getByText(/mcp\/u\//i)).toBeInTheDocument();
    expect(screen.getByText(/eth_live_/i)).toBeInTheDocument();
    expect(screen.getByText("Abre tu cliente de IA")).toBeInTheDocument();
  });

  it("responde a una consulta y muestra el panel técnico", () => {
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
