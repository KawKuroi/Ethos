import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ThemeProvider } from "@/components/theme-provider";
import { Settings } from "./settings";

const deleteAllData = vi.fn();
const requestAccountDeletion = vi.fn();
const getAccountDeletion = vi.fn();
const undoAccountDeletion = vi.fn();
const updateUser = vi.fn();

vi.mock("@/lib/api", () => ({
  deleteAllData: () => deleteAllData(),
  requestAccountDeletion: () => requestAccountDeletion(),
  getAccountDeletion: () => getAccountDeletion(),
  undoAccountDeletion: () => undoAccountDeletion(),
}));

vi.mock("@/lib/use-user", () => ({
  useUser: () => ({ name: "Axel", email: "axel@correo.com" }),
}));

vi.mock("@/lib/supabase/client", () => ({
  getBrowserClient: () => ({
    auth: { updateUser: (body: unknown) => updateUser(body) },
  }),
}));

function renderSettings() {
  return render(
    <ThemeProvider>
      <Settings />
    </ThemeProvider>,
  );
}

describe("Settings", () => {
  beforeEach(() => {
    deleteAllData.mockReset();
    requestAccountDeletion.mockReset();
    getAccountDeletion.mockReset().mockResolvedValue({ scheduled: false, purge_after: null });
    undoAccountDeletion.mockReset();
    updateUser.mockReset();
  });

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

  it("muestra el nombre de la sesión y el correo en solo lectura", () => {
    renderSettings();
    expect(screen.getByLabelText("Nombre")).toHaveValue("Axel");
    const email = screen.getByLabelText("Correo");
    expect(email).toHaveValue("axel@correo.com");
    expect(email).toBeDisabled();
    expect(screen.queryByLabelText("Usuario")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Zona horaria")).not.toBeInTheDocument();
  });

  it("guarda el nombre editado en Supabase", async () => {
    updateUser.mockResolvedValueOnce({ error: null });
    renderSettings();
    fireEvent.change(screen.getByLabelText("Nombre"), {
      target: { value: "Axel HR" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() =>
      expect(updateUser).toHaveBeenCalledWith({
        data: { full_name: "Axel HR" },
      }),
    );
    expect(await screen.findByText(/guardado/i)).toBeInTheDocument();
  });

  it("elimina los datos tras confirmar en el diálogo", async () => {
    deleteAllData.mockResolvedValueOnce(undefined);
    renderSettings();
    fireEvent.click(screen.getByRole("button", { name: "Eliminar datos" }));
    const dialog = screen.getByRole("dialog");
    fireEvent.click(within(dialog).getByRole("button", { name: "Eliminar datos" }));

    await waitFor(() => expect(deleteAllData).toHaveBeenCalled());
    expect(await screen.findByText(/datos eliminados/i)).toBeInTheDocument();
  });

  it("programa el borrado de cuenta y permite deshacerlo", async () => {
    requestAccountDeletion.mockResolvedValueOnce({
      scheduled: true,
      purge_after: "2026-08-05T00:00:00Z",
    });
    undoAccountDeletion.mockResolvedValueOnce(undefined);
    renderSettings();

    fireEvent.click(screen.getByRole("button", { name: "Eliminar cuenta" }));
    const dialog = screen.getByRole("dialog");
    fireEvent.click(within(dialog).getByRole("button", { name: "Eliminar cuenta" }));

    expect(await screen.findByText(/borrado programado/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Deshacer" }));
    await waitFor(() => expect(undoAccountDeletion).toHaveBeenCalled());
    expect(await screen.findByText(/borrado cancelado/i)).toBeInTheDocument();
  });

  it("muestra el borrado ya programado al cargar", async () => {
    getAccountDeletion.mockResolvedValue({
      scheduled: true,
      purge_after: "2026-08-05T00:00:00Z",
    });
    renderSettings();
    expect(await screen.findByText(/borrado programado/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Deshacer" })).toBeInTheDocument();
  });
});
