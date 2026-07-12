import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { QuickNav } from "./quick-nav";

const mocks = vi.hoisted(() => ({ pathname: "/app", push: vi.fn() }));

vi.mock("next/navigation", () => ({
  usePathname: () => mocks.pathname,
  useRouter: () => ({ push: mocks.push }),
}));

describe("QuickNav", () => {
  beforeEach(() => {
    mocks.pathname = "/app";
    mocks.push.mockClear();
  });

  it("abre la paleta con el botón y lista pantallas y categorías", () => {
    render(<QuickNav />);
    fireEvent.click(screen.getByRole("button", { name: /ir a/i }));
    expect(screen.getByRole("dialog", { name: "Ir a" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /fuentes/i })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /juegos/i })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /ajustes/i })).toBeInTheDocument();
  });

  it("abre con Ctrl+K, filtra sin acentos y navega con Enter", () => {
    render(<QuickNav />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    const input = screen.getByLabelText("Buscar destino");
    fireEvent.change(input, { target: { value: "musica" } });
    expect(screen.getByRole("option", { name: /música/i })).toBeInTheDocument();
    expect(screen.queryByRole("option", { name: /fuentes/i })).not.toBeInTheDocument();
    fireEvent.keyDown(input, { key: "Enter" });
    expect(mocks.push).toHaveBeenCalledWith("/app/categoria/music");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("mueve el resaltado con las flechas y cierra con Escape", () => {
    render(<QuickNav />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    const input = screen.getByLabelText("Buscar destino");
    fireEvent.keyDown(input, { key: "ArrowDown" });
    fireEvent.keyDown(input, { key: "Enter" });
    // Segunda opción: Fuentes (la primera es Inicio).
    expect(mocks.push).toHaveBeenCalledWith("/app/fuentes");

    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    fireEvent.keyDown(screen.getByLabelText("Buscar destino"), { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("navega con el cordal g + tecla a pantallas y categorías", () => {
    render(<QuickNav />);
    fireEvent.keyDown(window, { key: "g" });
    fireEvent.keyDown(window, { key: "f" });
    expect(mocks.push).toHaveBeenCalledWith("/app/fuentes");

    fireEvent.keyDown(window, { key: "g" });
    fireEvent.keyDown(window, { key: "3" });
    expect(mocks.push).toHaveBeenCalledWith("/app/categoria/film");
  });

  it("recorre las categorías con ] y [ con ciclo en los extremos", () => {
    mocks.pathname = "/app/categoria/games";
    render(<QuickNav />);
    fireEvent.keyDown(window, { key: "]" });
    expect(mocks.push).toHaveBeenCalledWith("/app/categoria/music");
    fireEvent.keyDown(window, { key: "[" });
    expect(mocks.push).toHaveBeenCalledWith("/app/categoria/books");
  });

  it("no reacciona a [ ] fuera de una categoría", () => {
    mocks.pathname = "/app/fuentes";
    render(<QuickNav />);
    fireEvent.keyDown(window, { key: "]" });
    expect(mocks.push).not.toHaveBeenCalled();
  });

  it("abre la ayuda de atajos con ? y la cierra con Escape", () => {
    render(<QuickNav />);
    fireEvent.keyDown(window, { key: "?" });
    expect(
      screen.getByRole("dialog", { name: /atajos de teclado/i }),
    ).toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("ignora los atajos mientras se escribe en un campo", () => {
    render(
      <>
        <input aria-label="campo externo" />
        <QuickNav />
      </>,
    );
    const field = screen.getByLabelText("campo externo");
    fireEvent.keyDown(field, { key: "g" });
    fireEvent.keyDown(field, { key: "f" });
    fireEvent.keyDown(field, { key: "?" });
    expect(mocks.push).not.toHaveBeenCalled();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
