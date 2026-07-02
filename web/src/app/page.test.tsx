import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider } from "@/components/theme-provider";
import Home from "./page";

describe("Home", () => {
  it("muestra la marca y el subtítulo", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: "Ethos" })).toBeInTheDocument();
    expect(screen.getByText(/tu gusto, hecho contexto/i)).toBeInTheDocument();
  });

  it("entra con la animación de pantalla del diseño", () => {
    render(<Home />);
    expect(screen.getByRole("main")).toHaveClass("eth-screen");
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
