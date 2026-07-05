"""Tests del resumen y los endpoints del slice de Libros (import, D47/D48)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.books.deps import get_books_store
from ethos_api.books.service import import_goodreads_csv
from ethos_api.books.store import InMemoryBooksStore
from ethos_api.books.summary import build_books_summary
from ethos_api.main import app
from tests.books.helpers import GOODREADS_CSV
from tests.helpers import auth_headers


def test_resumen_agrega_leidos_paginas_y_autores() -> None:
    store = InMemoryBooksStore()
    import_goodreads_csv("user-1", GOODREADS_CSV, store)
    summary = build_books_summary(store.items_for_user("user-1"))
    assert summary.books_read == 2
    assert summary.pages_read == 662 + 412
    assert [c.title for c in summary.currently_reading] == ["Project Hail Mary"]
    assert summary.wishlisted == 1
    assert {a.name for a in summary.top_authors} == {"Patrick Rothfuss", "Frank Herbert"}
    # La lectura más reciente por Date Read va primero.
    assert summary.recent_reads[0].title == "El nombre del viento"
    assert summary.recent_reads[0].rating == 100


@pytest.fixture
def client(jwt_secret: str) -> Iterator[tuple[TestClient, InMemoryBooksStore]]:
    store = InMemoryBooksStore()
    app.dependency_overrides[get_books_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client, store
    app.dependency_overrides.clear()


def _import(test_client: TestClient, user: str = "user-1") -> None:
    respuesta = test_client.post(
        "/sources/goodreads/import",
        content=GOODREADS_CSV.encode(),
        headers={**auth_headers(user), "Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["items"] == 4


def test_import_puebla_el_estado_y_el_resumen(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    _import(test_client)
    estado = test_client.get("/sources/books", headers=auth_headers()).json()
    assert estado["state"] == "fresh"
    assert estado["summary"]["books_read"] == 2
    assert estado["summary"]["pages_read"] == 1074


def test_import_invalido_da_422_y_no_toca_datos(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, store = client
    _import(test_client)
    respuesta = test_client.post(
        "/sources/goodreads/import",
        content=b"col1,col2\n1,2\n",
        headers={**auth_headers(), "Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 422
    # El import fallido no debe borrar el import anterior.
    assert len(store.items_for_user("user-1")) == 4


def test_descarga_de_contexto_de_libros(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    _import(test_client)
    respuesta = test_client.get("/context/books", headers=auth_headers())
    assert respuesta.status_code == 200
    assert (
        respuesta.headers["content-disposition"]
        == 'attachment; filename="books.context.json"'
    )
    contexto = respuesta.json()
    assert contexto["namespace"] == "books.*"
    assert contexto["provider"] == "goodreads"


def test_contexto_sin_datos_da_404(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.get("/context/books", headers=auth_headers("nadie"))
    assert respuesta.status_code == 404


def test_los_datos_no_se_cruzan_entre_usuarios(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    _import(test_client, "user-1")
    ajeno = test_client.get("/sources/books", headers=auth_headers("user-2")).json()
    assert ajeno["state"] == "never"
