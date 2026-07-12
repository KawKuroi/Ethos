import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ConnectHub } from "./connect-hub";

const mocks = vi.hoisted(() => ({
  connectSource: vi.fn(() => Promise.resolve()),
}));

vi.mock("@/lib/api", () => ({
  connectSource: mocks.connectSource,
  importFile: () => Promise.resolve({}),
  ApiError: class ApiError extends Error {},
}));

describe("ConnectHub", () => {
  it("lista los proveedores de la categoría con su modo", () => {
    render(<ConnectHub slug="music" onConnected={() => {}} />);
    expect(screen.getByRole("radio", { name: /listenbrainz/i })).toBeChecked();
    expect(screen.getByRole("radio", { name: /spotify/i })).toBeInTheDocument();
    // El proveedor por defecto muestra su guía paso a paso con enlaces.
    expect(
      screen.getByLabelText(/cómo conectar listenbrainz/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /listenbrainz\.org/i })).toHaveAttribute(
      "href",
      "https://listenbrainz.org/",
    );
  });

  it("al elegir un proveedor de import muestra su guía y el botón de subida", () => {
    render(<ConnectHub slug="music" onConnected={() => {}} />);
    fireEvent.click(screen.getByRole("radio", { name: /spotify/i }));
    expect(screen.getByLabelText(/cómo conectar spotify/i)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /spotify\.com\/account\/privacy/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /subir export/i })).toBeInTheDocument();
  });

  it("conecta por username con el proveedor elegido", async () => {
    render(<ConnectHub slug="anime" onConnected={() => {}} />);
    fireEvent.click(screen.getByRole("radio", { name: /kitsu/i }));
    fireEvent.change(screen.getByLabelText(/tu usuario de kitsu/i), {
      target: { value: "otaku" },
    });
    fireEvent.click(screen.getByRole("button", { name: /conectar/i }));
    await vi.waitFor(() =>
      expect(mocks.connectSource).toHaveBeenCalledWith("kitsu", "otaku"),
    );
  });

  it("avisa del reemplazo al cambiar de proveedor", () => {
    render(
      <ConnectHub slug="books" currentProvider="goodreads" onConnected={() => {}} />,
    );
    fireEvent.click(screen.getByRole("radio", { name: /hardcover/i }));
    expect(screen.getByRole("note")).toHaveTextContent(
      /reemplaza los datos actuales de Goodreads/i,
    );
  });

  it("los proveedores pendientes aparecen deshabilitados", () => {
    render(<ConnectHub slug="games" onConnected={() => {}} />);
    expect(screen.getByRole("radio", { name: /xbox/i })).toBeDisabled();
    expect(screen.getByRole("radio", { name: /playstation/i })).toBeDisabled();
  });
});
