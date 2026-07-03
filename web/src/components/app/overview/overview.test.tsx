import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Overview } from "./overview";

describe("Overview", () => {
  it("muestra el banner de IA sin conectar", () => {
    render(<Overview />);
    expect(
      screen.getByText(/tu ia aún no está conectada/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /conectar ia/i }),
    ).toHaveAttribute("href", "/app/conectar-ia");
  });

  it("muestra el stat band con cuatro cifras", () => {
    render(<Overview />);
    expect(screen.getByText(/el gusto en números/i)).toBeInTheDocument();
    for (const label of ["juegos", "horas", "deseados", "completado"]) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
  });

  it("muestra Juegos activa y categorías en desarrollo en el panorama", () => {
    render(<Overview />);
    expect(screen.getByText("Panorama · por actividad")).toBeInTheDocument();
    // Juegos como fila activa: su valor hero (también en el stat band).
    expect(screen.getAllByText("1.840").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("horas jugadas")).toBeInTheDocument();
    // Al menos una categoría en desarrollo.
    expect(screen.getAllByText(/en desarrollo · próximamente/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Anime y manga")).toBeInTheDocument();
  });

  it("muestra la actividad reciente", () => {
    render(<Overview />);
    expect(screen.getByText("Actividad reciente")).toBeInTheDocument();
    expect(screen.getByText(/jugaste a balatro/i)).toBeInTheDocument();
  });
});
