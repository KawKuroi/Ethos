import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Walkthrough } from "./walkthrough";
import styles from "./landing.module.css";

describe("Walkthrough", () => {
  it("arranca en el paso 1 y cambia de panel al pulsar el rail", () => {
    render(<Walkthrough />);

    expect(screen.getByTestId("walk-panel-0").className).toContain(
      styles.panelOn,
    );
    expect(screen.getByTestId("walk-panel-3").className).not.toContain(
      styles.panelOn,
    );

    fireEvent.click(
      screen.getByRole("button", { name: /tu ia la usa/i }),
    );

    expect(screen.getByTestId("walk-panel-3").className).toContain(
      styles.panelOn,
    );
    expect(screen.getByTestId("walk-panel-0").className).not.toContain(
      styles.panelOn,
    );
  });

  it("muestra los 4 pasos del recorrido", () => {
    render(<Walkthrough />);
    expect(screen.getByText("Conectas la fuente")).toBeInTheDocument();
    expect(screen.getByText("Ethos la normaliza")).toBeInTheDocument();
    expect(screen.getByText("Queda como categoría")).toBeInTheDocument();
    expect(screen.getByText("Tu IA la usa")).toBeInTheDocument();
    expect(screen.getByText(/reproduciendo en bucle/i)).toBeInTheDocument();
  });
});
