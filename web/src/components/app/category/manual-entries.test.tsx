import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ManualItem } from "@/lib/api";
import { ManualEntries } from "./manual-entries";

const listManualItems = vi.fn();
const addManualItem = vi.fn();
const deleteManualItem = vi.fn();

vi.mock("@/lib/api", () => ({
  listManualItems: (slug: string) => listManualItems(slug),
  addManualItem: (body: unknown) => addManualItem(body),
  deleteManualItem: (slug: string, id: string) => deleteManualItem(slug, id),
}));

const sample: ManualItem = {
  external_id: "manual:abc",
  category: "books",
  title: "Un libro a mano",
  status: "consumed",
  creators: [],
  year: null,
  rating: null,
  review: null,
  favorite: false,
};

describe("ManualEntries", () => {
  beforeEach(() => {
    listManualItems.mockReset();
    addManualItem.mockReset();
    deleteManualItem.mockReset();
  });

  it("lista las entradas a mano existentes", async () => {
    listManualItems.mockResolvedValueOnce([sample]);
    render(<ManualEntries slug="books" accent="#2f9e6b" />);
    expect(await screen.findByText("Un libro a mano")).toBeInTheDocument();
  });

  it("añade una entrada y avisa al padre", async () => {
    listManualItems.mockResolvedValueOnce([]);
    addManualItem.mockResolvedValueOnce({ ...sample, title: "Nuevo" });
    const onChange = vi.fn();
    render(<ManualEntries slug="books" accent="#2f9e6b" onChange={onChange} />);

    fireEvent.click(screen.getByRole("button", { name: /añadir \+/i }));
    fireEvent.change(screen.getByLabelText("Título"), { target: { value: "Nuevo" } });
    fireEvent.click(screen.getByRole("button", { name: /^añadir$/i }));

    await waitFor(() => expect(addManualItem).toHaveBeenCalled());
    expect(onChange).toHaveBeenCalled();
    expect(await screen.findByText("Nuevo")).toBeInTheDocument();
  });

  it("borra una entrada", async () => {
    listManualItems.mockResolvedValueOnce([sample]);
    deleteManualItem.mockResolvedValueOnce(undefined);
    render(<ManualEntries slug="books" accent="#2f9e6b" />);

    const remove = await screen.findByRole("button", { name: /borrar un libro a mano/i });
    fireEvent.click(remove);

    await waitFor(() => expect(deleteManualItem).toHaveBeenCalledWith("books", "manual:abc"));
  });
});
