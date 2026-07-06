import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Help } from "./help";

const submitFeedback = vi.fn();

vi.mock("@/lib/api", () => ({
  submitFeedback: (body: unknown) => submitFeedback(body),
}));

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

  it("confirma el envío de una sugerencia", async () => {
    submitFeedback.mockResolvedValueOnce(undefined);
    render(<Help />);
    fireEvent.change(screen.getByLabelText(/tu sugerencia/i), {
      target: { value: "Añadid Spotify" },
    });
    fireEvent.click(screen.getByRole("button", { name: /enviar/i }));
    expect(
      await screen.findByRole("button", { name: /enviado/i }),
    ).toBeInTheDocument();
    expect(submitFeedback).toHaveBeenCalledWith({ message: "Añadid Spotify" });
  });
});
