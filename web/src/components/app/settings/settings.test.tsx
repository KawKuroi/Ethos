import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemeProvider } from "@/components/theme-provider";
import { Settings } from "./settings";

function renderSettings() {
  return render(
    <ThemeProvider>
      <Settings />
    </ThemeProvider>,
  );
}

describe("Settings", () => {
  it("muestra las secciones de ajustes", () => {
    renderSettings();
    expect(screen.getByText("Perfil")).toBeInTheDocument();
    expect(screen.getByText("Apariencia")).toBeInTheDocument();
    expect(screen.getByText("Zona de peligro")).toBeInTheDocument();
    for (const label of ["Claro", "Oscuro", "Sistema"]) {
      expect(
        screen.getByRole("button", { name: new RegExp(label, "i") }),
      ).toBeInTheDocument();
    }
  });

  it("confirma la eliminación de cuenta con un diálogo", () => {
    renderSettings();
    fireEvent.click(
      screen.getByRole("button", { name: "Eliminar cuenta" }),
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    // Confirmar (dentro del diálogo) muestra el aviso de backend pendiente.
    fireEvent.click(
      within(dialog).getByRole("button", { name: "Eliminar cuenta" }),
    );
    expect(screen.getByText(/llegará con el backend/i)).toBeInTheDocument();
  });
});
