import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CategoryDetail } from "./category-detail";
import { CATEGORY_DETAIL } from "./data";

describe("CategoryDetail", () => {
  it("muestra los datos de Juegos (conectada)", () => {
    render(<CategoryDetail category={CATEGORY_DETAIL.games} />);
    expect(
      screen.getByRole("heading", { name: "Juegos" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Stardew Valley")).toBeInTheDocument();
    expect(screen.getByText("312")).toBeInTheDocument();
    expect(screen.getByText("Operativa")).toBeInTheDocument();
  });

  it("abre el modal de descarga y alterna JSON/MCP", () => {
    render(<CategoryDetail category={CATEGORY_DETAIL.games} />);
    fireEvent.click(
      screen.getByRole("button", { name: /descargar contexto/i }),
    );
    const dialog = screen.getByRole("dialog");
    const pre = dialog.querySelector("pre");
    expect(pre?.textContent).toContain('"namespace": "games.*"');

    fireEvent.click(within(dialog).getByRole("button", { name: "MCP" }));
    expect(dialog.querySelector("pre")?.textContent).toContain(
      "ethos.context(",
    );
  });

  it("muestra el estado en desarrollo para una categoría soon", () => {
    render(<CategoryDetail category={CATEGORY_DETAIL.film} />);
    expect(
      screen.getByText(/esta categoría está en desarrollo/i),
    ).toBeInTheDocument();
    expect(screen.getAllByText(/trakt/i).length).toBeGreaterThan(0);
  });
});
