import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CategoryPager } from "./category-pager";

describe("CategoryPager", () => {
  it("enlaza a la categoría anterior y a la siguiente", () => {
    render(<CategoryPager slug="music" />);
    expect(screen.getByRole("link", { name: /anterior/i })).toHaveAttribute(
      "href",
      "/app/categoria/games",
    );
    expect(screen.getByRole("link", { name: /siguiente/i })).toHaveAttribute(
      "href",
      "/app/categoria/film",
    );
  });

  it("cicla en los extremos del catálogo", () => {
    render(<CategoryPager slug="games" />);
    // La anterior a la primera es la última (Libros) y viceversa.
    expect(screen.getByRole("link", { name: /anterior/i })).toHaveAttribute(
      "href",
      "/app/categoria/books",
    );
    expect(screen.getByRole("link", { name: /siguiente/i })).toHaveAttribute(
      "href",
      "/app/categoria/music",
    );
  });

  it("no pinta nada con un slug desconocido", () => {
    const { container } = render(<CategoryPager slug="desconocida" />);
    expect(container).toBeEmptyDOMElement();
  });
});
