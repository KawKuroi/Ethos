import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Sidebar } from "./sidebar";

const mocks = vi.hoisted(() => ({ pathname: "/app" }));

vi.mock("next/navigation", () => ({
  usePathname: () => mocks.pathname,
}));

vi.mock("@/lib/use-user", () => ({
  useUser: () => ({ name: "Axel", email: "axel@correo.com" }),
}));

describe("Sidebar", () => {
  beforeEach(() => {
    mocks.pathname = "/app";
  });

  it("muestra los cuatro destinos de navegación", () => {
    render(<Sidebar />);
    for (const label of ["Inicio", "Fuentes", "Conectar IA", "Ayuda"]) {
      expect(
        screen.getByRole("link", { name: new RegExp(label, "i") }),
      ).toBeInTheDocument();
    }
  });

  it("resalta la ruta activa y no las demás", () => {
    mocks.pathname = "/app/fuentes";
    render(<Sidebar />);
    expect(screen.getByRole("link", { name: /fuentes/i })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: /inicio/i })).not.toHaveAttribute(
      "aria-current",
    );
  });

  it("muestra el nombre de la sesión sin el correo y enlaza el logo a la landing", () => {
    render(<Sidebar />);
    expect(screen.getByText("Axel")).toBeInTheDocument();
    expect(screen.queryByText("axel@correo.com")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ethos" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("muestra el badge pulsante en Conectar IA sin conexión", () => {
    const { container } = render(<Sidebar />);
    expect(
      container.querySelector('[aria-label="IA sin conectar"]'),
    ).not.toBeNull();
  });

  it("lista las cinco categorías como enlaces directos", () => {
    render(<Sidebar />);
    for (const [name, slug] of [
      ["Juegos", "games"],
      ["Música", "music"],
      ["Cine y TV", "film"],
      ["Anime y manga", "anime"],
      ["Libros", "books"],
    ]) {
      expect(
        screen.getByRole("link", { name: new RegExp(name, "i") }),
      ).toHaveAttribute("href", `/app/categoria/${slug}`);
    }
  });

  it("dentro de una categoría resalta su entrada y no Inicio", () => {
    mocks.pathname = "/app/categoria/music";
    render(<Sidebar />);
    expect(screen.getByRole("link", { name: /música/i })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: /inicio/i })).not.toHaveAttribute(
      "aria-current",
    );
  });
});
