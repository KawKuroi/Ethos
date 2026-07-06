import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { NotifyForm } from "./notify-form";

const register = vi.fn();

vi.mock("@/lib/api", () => ({
  ApiError: class ApiError extends Error {},
  registerCategoryInterest: (category: string, email: string) => register(category, email),
}));

describe("NotifyForm", () => {
  it("registra el interés y confirma con el correo", async () => {
    register.mockResolvedValueOnce(undefined);
    render(<NotifyForm category="places" defaultEmail="ana@example.com" />);

    fireEvent.click(screen.getByRole("button", { name: /avísame/i }));

    await waitFor(() =>
      expect(register).toHaveBeenCalledWith("places", "ana@example.com"),
    );
    expect(await screen.findByText(/te avisaremos/i)).toBeInTheDocument();
    expect(screen.getByText("ana@example.com")).toBeInTheDocument();
  });

  it("muestra un error si el registro falla", async () => {
    register.mockRejectedValueOnce(new Error("boom"));
    render(<NotifyForm category="food" defaultEmail="leo@example.com" />);

    fireEvent.click(screen.getByRole("button", { name: /avísame/i }));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
