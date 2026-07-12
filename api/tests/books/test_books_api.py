"""Tests del resumen y los endpoints del slice de Libros (import, D47/D48)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from pydantic import SecretStr

from ethos_api.books.deps import (
    get_books_store,
    get_hardcover_client,
    get_openlibrary_client,
)
from ethos_api.books.service import import_goodreads_csv
from ethos_api.books.store import InMemoryBooksStore
from ethos_api.books.summary import build_books_summary
from ethos_api.config import settings
from ethos_api.credentials.deps import get_repository
from ethos_api.credentials.repository import InMemoryCredentialRepository
from ethos_api.main import app
from tests.books.helpers import (
    GOODREADS_CSV,
    STORYGRAPH_CSV,
    FakeHardcoverApi,
    FakeOpenLibraryApi,
)
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
def client(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> Iterator[tuple[TestClient, InMemoryBooksStore]]:
    monkeypatch.setattr(
        settings, "encryption_key", SecretStr(Fernet.generate_key().decode())
    )
    store = InMemoryBooksStore()
    repo = InMemoryCredentialRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_books_store] = lambda: store
    app.dependency_overrides[get_openlibrary_client] = FakeOpenLibraryApi
    app.dependency_overrides[get_hardcover_client] = FakeHardcoverApi
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
    assert contexto["namespace"] == "books_*"
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


def test_import_de_storygraph_reemplaza_y_reporta_proveedor(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    _import(test_client)  # Goodreads: 4 libros
    respuesta = test_client.post(
        "/sources/storygraph/import",
        content=STORYGRAPH_CSV.encode(),
        headers={**auth_headers(), "Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["items"] == 3
    estado = test_client.get("/sources/books", headers=auth_headers()).json()
    assert estado["provider"] == "storygraph"
    assert estado["mode"] == "import"
    assert estado["summary"]["books_read"] == 1


def test_conectar_openlibrary_refresca_y_reporta_proveedor(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post(
        "/sources/openlibrary",
        json={"user_name": "lectora"},
        headers=auth_headers(),
    )
    assert respuesta.status_code == 201
    estado = test_client.get("/sources/books", headers=auth_headers()).json()
    assert estado["state"] == "fresh"
    assert estado["provider"] == "openlibrary"
    assert estado["mode"] == "api"
    assert estado["summary"]["books_read"] == 1


def test_openlibrary_privado_deja_estado_privado(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    app.dependency_overrides[get_openlibrary_client] = lambda: FakeOpenLibraryApi(
        status_code=403
    )
    test_client.post(
        "/sources/openlibrary", json={"user_name": "privada"}, headers=auth_headers()
    )
    estado = test_client.get("/sources/books", headers=auth_headers()).json()
    assert estado["state"] == "private"
    assert "Open Library" in estado["detail"]


def test_conectar_hardcover_con_token(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post(
        "/sources/hardcover",
        json={"token": "token-123456"},
        headers=auth_headers(),
    )
    assert respuesta.status_code == 201
    estado = test_client.get("/sources/books", headers=auth_headers()).json()
    assert estado["state"] == "fresh"
    assert estado["provider"] == "hardcover"
    assert estado["summary"]["books_read"] == 1


def test_hardcover_token_caducado_deja_estado_privado(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    app.dependency_overrides[get_hardcover_client] = lambda: FakeHardcoverApi(
        status_code=401
    )
    test_client.post(
        "/sources/hardcover", json={"token": "token-caduco"}, headers=auth_headers()
    )
    estado = test_client.get("/sources/books", headers=auth_headers()).json()
    assert estado["state"] == "private"
    assert "Hardcover" in estado["detail"]


def test_refresh_openlibrary_y_hardcover_sin_conectar_dan_404(
    client: tuple[TestClient, InMemoryBooksStore],
) -> None:
    test_client, _ = client
    assert (
        test_client.post(
            "/sources/openlibrary/refresh", headers=auth_headers()
        ).status_code
        == 404
    )
    assert (
        test_client.post(
            "/sources/hardcover/refresh", headers=auth_headers()
        ).status_code
        == 404
    )
