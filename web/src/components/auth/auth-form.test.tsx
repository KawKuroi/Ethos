import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthForm } from "./auth-form";

const mocks = vi.hoisted(() => ({
  signInWithPassword: vi.fn(),
  signUp: vi.fn(),
  signInWithOAuth: vi.fn(),
  push: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mocks.push }),
}));

vi.mock("@/lib/supabase/client", () => ({
  getBrowserClient: () => ({
    auth: {
      signInWithPassword: mocks.signInWithPassword,
      signUp: mocks.signUp,
      signInWithOAuth: mocks.signInWithOAuth,
    },
  }),
}));

function submitForm(container: HTMLElement) {
  const form = container.querySelector("form");
  expect(form).not.toBeNull();
  fireEvent.submit(form as HTMLFormElement);
}

describe("AuthForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.signInWithPassword.mockResolvedValue({ error: null });
    mocks.signUp.mockResolvedValue({ data: { session: null }, error: null });
    mocks.signInWithOAuth.mockResolvedValue({ error: null });
  });

  it("alterna a registro mostrando el campo Nombre", () => {
    render(<AuthForm />);
    expect(screen.queryByPlaceholderText("Cómo te llamamos")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));

    expect(screen.getByPlaceholderText("Cómo te llamamos")).toBeInTheDocument();
  });

  it("muestra u oculta la contraseña", () => {
    render(<AuthForm />);
    const pw = screen.getByPlaceholderText("Tu contraseña");
    expect(pw).toHaveAttribute("type", "password");

    fireEvent.click(
      screen.getByRole("button", { name: /mostrar u ocultar contraseña/i }),
    );
    expect(pw).toHaveAttribute("type", "text");
  });

  it("rechaza contraseñas de menos de 8 caracteres", () => {
    const { container } = render(<AuthForm />);
    fireEvent.change(screen.getByPlaceholderText("tu@correo.com"), {
      target: { value: "a@b.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Tu contraseña"), {
      target: { value: "123" },
    });
    submitForm(container);

    expect(screen.getByText(/al menos 8 caracteres/i)).toBeInTheDocument();
    expect(mocks.signInWithPassword).not.toHaveBeenCalled();
  });

  it("registra sin exigir términos (no existen en el producto)", async () => {
    const { container } = render(<AuthForm />);
    fireEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
    fireEvent.change(screen.getByPlaceholderText("Cómo te llamamos"), {
      target: { value: "Ada" },
    });
    fireEvent.change(screen.getByPlaceholderText("tu@correo.com"), {
      target: { value: "a@b.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Mínimo 8 caracteres"), {
      target: { value: "12345678" },
    });
    submitForm(container);

    await waitFor(() => expect(mocks.signUp).toHaveBeenCalled());
    expect(screen.queryByText(/términos/i)).toBeNull();
  });

  it("inicia sesión con correo y contraseña válidos y redirige a la app", async () => {
    const { container } = render(<AuthForm />);
    fireEvent.change(screen.getByPlaceholderText("tu@correo.com"), {
      target: { value: "a@b.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Tu contraseña"), {
      target: { value: "12345678" },
    });
    submitForm(container);

    await waitFor(() =>
      expect(mocks.signInWithPassword).toHaveBeenCalledWith({
        email: "a@b.com",
        password: "12345678",
      }),
    );
    await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/app"));
  });

  it("lanza OAuth con el proveedor elegido", async () => {
    render(<AuthForm />);
    fireEvent.click(screen.getByRole("button", { name: /continuar con github/i }));

    await waitFor(() =>
      expect(mocks.signInWithOAuth).toHaveBeenCalledWith(
        expect.objectContaining({ provider: "github" }),
      ),
    );
  });
});
