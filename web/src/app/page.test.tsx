import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider } from "@/components/theme-provider";
import Home from "./page";

describe("Landing", () => {
  it("muestra el titular del hero", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { level: 1, name: /reúne lo que te gusta/i }),
    ).toBeInTheDocument();
  });

  it("explica qué es un MCP", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { name: /qué es un mcp/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/protocolo mcp/i)).toBeInTheDocument();
  });

  it("recorre una categoría y enseña el catálogo completo", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { name: /una categoría, de tu app hasta tu ia/i }),
    ).toBeInTheDocument();
    // Las 5 categorías del catálogo activo (D27, ajustado por D31) están en la galería.
    for (const name of [
      "Juegos",
      "Música",
      "Cine y TV",
      "Anime y manga",
      "Libros",
    ]) {
      expect(screen.getAllByText(name).length).toBeGreaterThan(0);
    }
    // Las diferidas se muestran "en desarrollo" con aviso (D50).
    for (const name of ["Lugares", "Comida", "Juegos de mesa"]) {
      expect(screen.getAllByText(name).length).toBeGreaterThan(0);
    }
    // La retirada (Actividad física, D31) no aparece.
    expect(screen.queryByText("Actividad física")).not.toBeInTheDocument();
  });

  it("muestra FAQ, sugerencias y footer", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { name: /preguntas frecuentes/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /enviar sugerencia/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/tu gusto, ordenado/i)).toBeInTheDocument();
  });

  it("los CTA apuntan a /auth y el GitHub al repo real", () => {
    render(<Home />);
    const authLinks = screen
      .getAllByRole("link")
      .filter((link) => link.getAttribute("href") === "/auth");
    expect(authLinks.length).toBeGreaterThanOrEqual(2);
    expect(screen.getByTitle("Ver en GitHub")).toHaveAttribute(
      "href",
      "https://github.com/KawKuroi/Ethos",
    );
  });
});

describe("ThemeProvider", () => {
  it("renderiza a sus hijos", () => {
    render(
      <ThemeProvider>
        <span>contenido</span>
      </ThemeProvider>,
    );
    expect(screen.getByText("contenido")).toBeInTheDocument();
  });
});
