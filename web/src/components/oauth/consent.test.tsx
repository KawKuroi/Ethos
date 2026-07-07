import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { OAuthConsent } from "./consent";

const approveOAuth = vi.fn();
const getSession = vi.fn();
let searchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useSearchParams: () => searchParams,
}));

vi.mock("@/lib/api", () => ({
  approveOAuth: (params: unknown, approve: boolean) => approveOAuth(params, approve),
  NotAuthenticatedError: class NotAuthenticatedError extends Error {},
}));

vi.mock("@/lib/supabase/client", () => ({
  getBrowserClient: () => ({ auth: { getSession } }),
}));

const VALID = new URLSearchParams({
  client_id: "eth_client_abc",
  client_name: "Claude",
  redirect_uri: "https://client.example/callback",
  code_challenge: "reto",
  state: "xyz",
});

describe("OAuthConsent", () => {
  beforeEach(() => {
    approveOAuth.mockReset();
    getSession.mockReset().mockResolvedValue({ data: { session: { user: {} } } });
    searchParams = VALID;
  });

  it("muestra el cliente y autoriza", async () => {
    approveOAuth.mockResolvedValueOnce("https://client.example/callback?code=c1");
    render(<OAuthConsent />);

    expect(await screen.findByText("Claude")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Autorizar" }));

    await waitFor(() =>
      expect(approveOAuth).toHaveBeenCalledWith(
        expect.objectContaining({ client_id: "eth_client_abc", state: "xyz" }),
        true,
      ),
    );
  });

  it("puede denegar el acceso", async () => {
    approveOAuth.mockResolvedValueOnce(
      "https://client.example/callback?error=access_denied",
    );
    render(<OAuthConsent />);

    fireEvent.click(await screen.findByRole("button", { name: "Denegar" }));
    await waitFor(() =>
      expect(approveOAuth).toHaveBeenCalledWith(expect.anything(), false),
    );
  });

  it("pide iniciar sesión si no hay sesión", async () => {
    getSession.mockResolvedValue({ data: { session: null } });
    render(<OAuthConsent />);
    expect(
      await screen.findByText(/inicia sesión para continuar/i),
    ).toBeInTheDocument();
  });

  it("rechaza solicitudes sin parámetros", () => {
    searchParams = new URLSearchParams();
    render(<OAuthConsent />);
    expect(screen.getByText(/solicitud inválida/i)).toBeInTheDocument();
  });
});
