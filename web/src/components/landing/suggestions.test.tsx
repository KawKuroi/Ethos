import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Suggestions } from "./suggestions";

describe("Suggestions", () => {
  it("muestra el efímero Enviado tras enviar", () => {
    const { container } = render(<Suggestions />);
    const form = container.querySelector("form");
    expect(form).not.toBeNull();

    fireEvent.submit(form as HTMLFormElement);

    expect(
      screen.getByRole("button", { name: /enviado/i }),
    ).toBeInTheDocument();
  });
});
