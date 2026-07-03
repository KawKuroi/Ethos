import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Sources } from "./sources";

describe("Sources", () => {
  it("muestra el resumen y los grupos", () => {
    render(<Sources />);
    expect(screen.getByText("activas")).toBeInTheDocument();
    expect(screen.getByText("en desarrollo")).toBeInTheDocument();
    expect(screen.getByText("Activas")).toBeInTheDocument();
  });

  it("lista Juegos en Activas con enlace al detalle", () => {
    render(<Sources />);
    const link = screen.getByRole("link", { name: /juegos/i });
    expect(link).toHaveAttribute("href", "/app/categoria/games");
  });

  it("lista las cuatro categorías en desarrollo", () => {
    render(<Sources />);
    for (const name of ["Música", "Cine y TV", "Anime y manga", "Libros"]) {
      expect(
        screen.getByRole("link", { name: new RegExp(name, "i") }),
      ).toBeInTheDocument();
    }
  });
});
