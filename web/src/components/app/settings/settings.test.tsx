import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ThemeProvider } from "@/components/theme-provider";
import { Settings } from "./settings";

const deleteAllData = vi.fn();
const requestAccountDeletion = vi.fn();
const getAccountDeletion = vi.fn();
const undoAccountDeletion = vi.fn();
const updateUser = vi.fn();
const signInWithPassword = vi.fn();
const signOut = vi.fn();
const goToLanding = vi.fn();
const exportAllContext = vi.fn();

vi.mock("@/lib/api", () => ({
  deleteAllData: () => deleteAllData(),
  requestAccountDeletion: () => requestAccountDeletion(),
  getAccountDeletion: () => getAccountDeletion(),
  undoAccountDeletion: () => undoAccountDeletion(),
  exportAllContext: (slugs: string[]) => exportAllContext(slugs),
}));

vi.mock("@/lib/use-user", () => ({
  useUser: () => ({
    name: "Axel",
    email: "axel@correo.com",
    providers: ["email"],
  }),
}));

vi.mock("@/lib/navigation", () => ({
  goToLanding: () => goToLanding(),
}));

vi.mock("@/lib/use-active-sources", () => ({
  useActiveSources: () => ({
    loading: false,
    gamesSummary: null,
    views: [
      { slug: "games", live: true, records: 312 },
      { slug: "music", live: true, records: 5210 },
      { slug: "books", live: false, records: 0 },
    ],
  }),
}));

vi.mock("@/lib/supabase/client", () => ({
  getBrowserClient: () => ({
    auth: {
      updateUser: (body: unknown) => updateUser(body),
      signInWithPassword: (body: unknown) => signInWithPassword(body),
      signOut: () => signOut(),
    },
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
    signInWithPassword.mockReset();
    signOut.mockReset().mockResolvedValue(undefined);
    goToLanding.mockReset();
    exportAllContext.mockReset().mockResolvedValue(undefined);
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

  it("reautentica y cambia la contraseña", async () => {
    signInWithPassword.mockResolvedValueOnce({ error: null });
    updateUser.mockResolvedValueOnce({ error: null });
    renderSettings();

    fireEvent.change(screen.getByLabelText("Contraseña actual"), {
      target: { value: "clave-antigua" },
    });
    fireEvent.change(screen.getByLabelText("Nueva contraseña"), {
      target: { value: "clave-nueva-123" },
    });
    fireEvent.change(screen.getByLabelText("Repite la nueva contraseña"), {
      target: { value: "clave-nueva-123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Cambiar contraseña" }));

    await waitFor(() =>
      expect(signInWithPassword).toHaveBeenCalledWith({
        email: "axel@correo.com",
        password: "clave-antigua",
      }),
    );
    await waitFor(() =>
      expect(updateUser).toHaveBeenCalledWith({ password: "clave-nueva-123" }),
    );
    expect(await screen.findByText(/contraseña cambiada/i)).toBeInTheDocument();
  });

  it("avisa si la contraseña actual es incorrecta", async () => {
    signInWithPassword.mockResolvedValueOnce({ error: { message: "invalid" } });
    renderSettings();

    fireEvent.change(screen.getByLabelText("Contraseña actual"), {
      target: { value: "mala" },
    });
    fireEvent.change(screen.getByLabelText("Nueva contraseña"), {
      target: { value: "clave-nueva-123" },
    });
    fireEvent.change(screen.getByLabelText("Repite la nueva contraseña"), {
      target: { value: "clave-nueva-123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Cambiar contraseña" }));

    expect(
      await screen.findByText(/la contraseña actual no es correcta/i),
    ).toBeInTheDocument();
    expect(updateUser).not.toHaveBeenCalled();
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

  it("programa el borrado de cuenta, cierra la sesión y vuelve a la landing", async () => {
    requestAccountDeletion.mockResolvedValueOnce({
      scheduled: true,
      purge_after: "2026-08-05T00:00:00Z",
    });
    renderSettings();

    fireEvent.click(screen.getByRole("button", { name: "Eliminar cuenta" }));
    const dialog = screen.getByRole("dialog");
    fireEvent.click(within(dialog).getByRole("button", { name: "Eliminar cuenta" }));

    await waitFor(() => expect(requestAccountDeletion).toHaveBeenCalled());
    await waitFor(() => expect(goToLanding).toHaveBeenCalled());
    expect(signOut).toHaveBeenCalled();
  });

  it("muestra el borrado ya programado al cargar y permite deshacerlo", async () => {
    getAccountDeletion.mockResolvedValue({
      scheduled: true,
      purge_after: "2026-08-05T00:00:00Z",
    });
    undoAccountDeletion.mockResolvedValueOnce(undefined);
    renderSettings();
    expect(await screen.findByText(/borrado programado/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Deshacer" }));
    await waitFor(() => expect(undoAccountDeletion).toHaveBeenCalled());
    expect(await screen.findByText(/borrado cancelado/i)).toBeInTheDocument();
  });

  it("muestra las cifras reales de fuentes y registros", () => {
    renderSettings();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("fuentes activas")).toBeInTheDocument();
    // es-ES no agrupa los números de 4 cifras (312 + 5210 = 5522).
    expect(screen.getByText("5522")).toBeInTheDocument();
    expect(screen.getByText("registros de contexto")).toBeInTheDocument();
  });

  it("exporta el contexto de las fuentes activas", async () => {
    renderSettings();
    fireEvent.click(
      screen.getByRole("button", { name: /descargar mis datos/i }),
    );

    await waitFor(() =>
      expect(exportAllContext).toHaveBeenCalledWith(["games", "music"]),
    );
    expect(await screen.findByText(/descarga lista/i)).toBeInTheDocument();
  });

  it("cierra la sesión y redirige a la landing", async () => {
    renderSettings();
    fireEvent.click(screen.getByRole("button", { name: "Cerrar sesión" }));
    await waitFor(() => expect(signOut).toHaveBeenCalled());
    await waitFor(() => expect(goToLanding).toHaveBeenCalled());
  });
});
