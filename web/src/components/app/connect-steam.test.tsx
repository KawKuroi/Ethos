import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ConnectSteamButton } from "./connect-steam";

const mocks = vi.hoisted(() => ({
  getSteamLoginUrl: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  getSteamLoginUrl: mocks.getSteamLoginUrl,
}));

describe("ConnectSteamButton", () => {
  it("pide el login con retorno a /steam/return (la página que existe)", async () => {
    // Fija el contrato con src/app/steam/return: un return_to a otra ruta
    // rompe el flujo completo (Steam devuelve a un 404).
    mocks.getSteamLoginUrl.mockResolvedValue(
      "https://steamcommunity.com/openid/login?openid.mode=checkid_setup",
    );
    render(<ConnectSteamButton />);
    fireEvent.click(screen.getByRole("button", { name: /conectar steam/i }));

    await waitFor(() =>
      expect(mocks.getSteamLoginUrl).toHaveBeenCalledWith(
        `${window.location.origin}/steam/return`,
      ),
    );
  });

  it("muestra el error si no se pudo iniciar la conexión", async () => {
    mocks.getSteamLoginUrl.mockRejectedValue(new Error("api caída"));
    render(<ConnectSteamButton />);
    fireEvent.click(screen.getByRole("button", { name: /conectar steam/i }));

    await waitFor(() =>
      expect(
        screen.getByText(/no se pudo iniciar la conexión con steam/i),
      ).toBeInTheDocument(),
    );
  });
});
