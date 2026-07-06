"""Tests de las entradas a mano (D51)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.books.deps import get_books_store
from ethos_api.books.service import import_goodreads_csv
from ethos_api.books.store import InMemoryBooksStore
from ethos_api.books.summary import build_books_summary
from ethos_api.games.deps import get_games_store
from ethos_api.games.store import InMemoryGamesStore
from ethos_api.items.models import ManualItemInput
from ethos_api.items.service import build_manual_item
from ethos_api.main import app
from ethos_api.schema import Category, ItemStatus
from tests.books.helpers import GOODREADS_CSV
from tests.helpers import auth_headers


@pytest.fixture
def client(
    jwt_secret: str,
) -> Iterator[tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore]]:
    books = InMemoryBooksStore()
    games = InMemoryGamesStore()
    app.dependency_overrides[get_books_store] = lambda: books
    app.dependency_overrides[get_games_store] = lambda: games
    with TestClient(app) as test_client:
        yield test_client, books, games
    app.dependency_overrides.clear()


def _add_book(test_client: TestClient, title: str = "Un libro a mano") -> dict[str, object]:
    body = {"category": "books", "title": title, "status": "consumed", "rating": 90}
    response = test_client.post("/items", json=body, headers=auth_headers())
    assert response.status_code == 201
    return response.json()


def test_add_list_and_delete(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, _ = client
    created = _add_book(test_client)
    assert created["external_id"].startswith("manual:")
    assert created["title"] == "Un libro a mano"

    listed = test_client.get("/items/books", headers=auth_headers()).json()
    assert len(listed) == 1

    deleted = test_client.delete(
        f"/items/books/{created['external_id']}", headers=auth_headers()
    )
    assert deleted.status_code == 204
    assert test_client.get("/items/books", headers=auth_headers()).json() == []


def test_manual_item_cuenta_en_el_resumen(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, books, _ = client
    _add_book(test_client, "Leído a mano")
    summary = build_books_summary(books.items_for_user("user-1"))
    # La entrada a mano (status consumed) cuenta como leído en el resumen.
    assert summary.books_read == 1


def test_refresco_conserva_las_entradas_a_mano(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, books, _ = client
    _add_book(test_client, "Sobrevive al refresco")
    # Un import (refresco de Libros) reemplaza lo del proveedor pero conserva
    # las entradas a mano.
    import_goodreads_csv("user-1", GOODREADS_CSV, books)
    titles = {i.work.title for i in books.items_for_user("user-1")}
    assert "Sobrevive al refresco" in titles
    assert "Dune" in titles


def test_aislamiento_por_usuario(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, _ = client
    _add_book(test_client)
    ajenos = test_client.get("/items/books", headers=auth_headers("user-2")).json()
    assert ajenos == []


def test_requiere_autenticacion(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, _ = client
    body = {"category": "books", "title": "x", "status": "consumed"}
    assert test_client.post("/items", json=body).status_code == 401


def test_categoria_sin_entradas_a_mano_rechazada(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, _ = client
    body = {"category": "music", "title": "x", "status": "consumed"}
    assert test_client.post("/items", json=body, headers=auth_headers()).status_code == 422


def test_borrar_id_no_manual_rechazado(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, _ = client
    respuesta = test_client.delete("/items/books/steam:440", headers=auth_headers())
    assert respuesta.status_code == 422


def test_borrar_inexistente_da_404(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, _ = client
    respuesta = test_client.delete("/items/books/manual:noexiste", headers=auth_headers())
    assert respuesta.status_code == 404


def test_entrada_manual_en_otra_categoria(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryGamesStore],
) -> None:
    test_client, _, games = client
    body = {"category": "games", "title": "Un juego físico", "status": "consumed"}
    response = test_client.post("/items", json=body, headers=auth_headers())
    assert response.status_code == 201
    assert games.items_for_user("user-1")[0].work.title == "Un juego físico"
    # No se cruza con Libros.
    assert test_client.get("/items/books", headers=auth_headers()).json() == []


def test_build_manual_item_marca_source() -> None:
    item = build_manual_item(
        ManualItemInput(category=Category.film, title="Peli", status=ItemStatus.consumed)
    )
    assert item.source == "manual"
    assert item.work.external_ids["manual_id"]
