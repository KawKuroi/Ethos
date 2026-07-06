"""Endpoints de entradas a mano (D51).

Añadir, listar y borrar registros sin proveedor en una categoría de obra. Las
entradas viven en `user_items` junto a las del proveedor (source `manual`), así
que ya cuentan en los resúmenes, el contexto descargable y las tools del MCP;
el refresco del proveedor las conserva.
"""

from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, HTTPException, status

from ethos_api.anime.deps import AnimeStoreDep
from ethos_api.auth import CurrentUserId
from ethos_api.books.deps import BooksStoreDep
from ethos_api.film.deps import FilmStoreDep
from ethos_api.games.deps import GamesStoreDep
from ethos_api.items.models import MANUAL_CATEGORIES, ManualItemInput, ManualItemOut
from ethos_api.items.service import build_manual_item, manual_items, to_out
from ethos_api.items.support import MANUAL_PREFIX
from ethos_api.schema import Category, NormalizedItem

router = APIRouter(prefix="/items", tags=["items"])


class ManualItemStore(Protocol):
    """Operaciones que la ruta de entradas a mano necesita de un store de items."""

    def add_item(self, user_id: str, item: NormalizedItem) -> None: ...

    def delete_item(self, user_id: str, external_id: str) -> bool: ...

    def items_for_user(self, user_id: str) -> list[NormalizedItem]: ...


def _resolve(
    category: Category,
    games: GamesStoreDep,
    film: FilmStoreDep,
    anime: AnimeStoreDep,
    books: BooksStoreDep,
) -> ManualItemStore:
    stores: dict[Category, ManualItemStore] = {
        Category.games: games,
        Category.film: film,
        Category.anime: anime,
        Category.books: books,
    }
    store = stores.get(category)
    if store is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Esa categoría no admite entradas a mano",
        )
    return store


@router.post("", response_model=ManualItemOut, status_code=status.HTTP_201_CREATED)
def add_manual_item(
    body: ManualItemInput,
    user_id: CurrentUserId,
    games: GamesStoreDep,
    film: FilmStoreDep,
    anime: AnimeStoreDep,
    books: BooksStoreDep,
) -> ManualItemOut:
    """Añade un registro a mano a la categoría indicada."""
    if body.category not in MANUAL_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Esa categoría no admite entradas a mano",
        )
    store = _resolve(body.category, games, film, anime, books)
    item = build_manual_item(body)
    store.add_item(user_id, item)
    return to_out(item)


@router.get("/{category}", response_model=list[ManualItemOut])
def list_manual_items(
    category: Category,
    user_id: CurrentUserId,
    games: GamesStoreDep,
    film: FilmStoreDep,
    anime: AnimeStoreDep,
    books: BooksStoreDep,
) -> list[ManualItemOut]:
    """Lista las entradas a mano de una categoría (sin las del proveedor)."""
    store = _resolve(category, games, film, anime, books)
    return manual_items(store.items_for_user(user_id))


@router.delete("/{category}/{external_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manual_item(
    category: Category,
    external_id: str,
    user_id: CurrentUserId,
    games: GamesStoreDep,
    film: FilmStoreDep,
    anime: AnimeStoreDep,
    books: BooksStoreDep,
) -> None:
    """Borra una entrada a mano por su `external_id` (`manual:<id>`)."""
    if not external_id.startswith(MANUAL_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo se pueden borrar entradas a mano",
        )
    store = _resolve(category, games, film, anime, books)
    if not store.delete_item(user_id, external_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una entrada a mano con ese id",
        )
