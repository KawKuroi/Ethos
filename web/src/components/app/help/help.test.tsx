import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Help } from "./help";

describe("Help", () => {
  it("abre y cierra el acordeón de FAQ", () => {
    render(<Help />);
    // El primero está abierto por defecto.
    expect(
      screen.getByText(/reúne tu gusto de muchas apps/i),
    ).toBeInTheDocument();
    // Abrir otra pregunta muestra su respuesta.
    fireEvent.click(
      screen.getByRole("button", { name: /cómo le doy mi contexto/i }),
    );
    expect(screen.getByText(/descargas los archivos de contexto/i)).toBeInTheDocument();
  });

  it("confirma el envío de una sugerencia", () => {
    render(<Help />);
    fireEvent.change(screen.getByLabelText(/tu sugerencia/i), {
      target: { value: "Añadid Spotify" },
    });
    fireEvent.click(screen.getByRole("button", { name: /enviar/i }));
    expect(
      screen.getByRole("button", { name: /enviado/i }),
    ).toBeInTheDocument();
  });
});
