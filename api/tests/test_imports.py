"""Tests del import genérico con autodetección (D49)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.books.deps import get_books_store
from ethos_api.books.store import InMemoryBooksStore
from ethos_api.imports.detection import detect_import
from ethos_api.main import app
from ethos_api.schema import Category
from tests.books.helpers import GOODREADS_CSV
from tests.helpers import auth_headers


def test_detecta_el_export_de_goodreads() -> None:
    signature = detect_import(GOODREADS_CSV)
    assert signature is not None
    assert signature.provider == "goodreads"
    assert signature.category is Category.books


def test_archivo_desconocido_no_se_detecta() -> None:
    assert detect_import("col1,col2\n1,2\n") is None
    assert detect_import("") is None
    assert detect_import("no es un csv") is None


@pytest.fixture
def client(jwt_secret: str) -> Iterator[tuple[TestClient, InMemoryBooksStore]]:
    store = InMemoryBooksStore()
    app.dependency_overrides[get_books_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client, store
    app.dependency_overrides.clear()


def test_import_generico_detecta_y_delega(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, store = client
    respuesta = test_client.post(
        "/imports",
        content=GOODREADS_CSV.encode(),
        headers={**auth_headers(), "Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["provider"] == "goodreads"
    assert datos["category"] == "books"
    assert datos["items"] == 4
    assert len(store.items_for_user("user-1")) == 4


def test_import_generico_desconocido_da_422_con_guia(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post(
        "/imports",
        content=b"col1,col2\n1,2\n",
        headers={**auth_headers(), "Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 422
    assert "Goodreads" in respuesta.json()["detail"]


def test_import_generico_requiere_sesion(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    assert test_client.post("/imports", content=b"x").status_code == 401
