import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Suggestions } from "./suggestions";

const submitFeedback = vi.fn();

vi.mock("@/lib/api", () => ({
  submitFeedback: (body: unknown) => submitFeedback(body),
}));

describe("Suggestions", () => {
  beforeEach(() => submitFeedback.mockReset());

  it("envía la sugerencia y muestra el efímero Enviado", async () => {
    submitFeedback.mockResolvedValueOnce(undefined);
    render(<Suggestions />);

    fireEvent.change(screen.getByLabelText(/tu sugerencia/i), {
      target: { value: "Añadid Spotify" },
    });
    fireEvent.click(screen.getByRole("button", { name: /enviar sugerencia/i }));

    expect(await screen.findByRole("button", { name: /enviado/i })).toBeInTheDocument();
    expect(submitFeedback).toHaveBeenCalledWith(
      expect.objectContaining({ message: "Añadid Spotify" }),
    );
  });

  it("no envía si la sugerencia está vacía", () => {
    render(<Suggestions />);
    fireEvent.click(screen.getByRole("button", { name: /enviar sugerencia/i }));
    expect(submitFeedback).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
