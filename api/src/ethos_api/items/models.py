"""Modelos de las entradas a mano (D51)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ethos_api.schema import Category, ItemStatus

# Categorías de obra que admiten entradas a mano (las de item). Música es de
# eventos (scrobbles), no de obras: queda fuera de las entradas a mano en v1.
MANUAL_CATEGORIES: frozenset[Category] = frozenset(
    {Category.games, Category.film, Category.anime, Category.books}
)


class ManualItemInput(BaseModel):
    """Entrada para añadir un registro a mano a una categoría."""

    category: Category
    title: str = Field(min_length=1, max_length=300)
    status: ItemStatus
    creators: list[str] = Field(default_factory=list)
    year: int | None = Field(default=None, ge=0, le=3000)
    rating: int | None = Field(default=None, ge=0, le=100)
    review: str | None = Field(default=None, max_length=2000)
    favorite: bool = False


class ManualItemOut(BaseModel):
    """Vista de una entrada a mano para la web."""

    external_id: str
    category: Category
    title: str
    status: ItemStatus
    creators: list[str]
    year: int | None
    rating: int | None
    review: str | None
    favorite: bool
