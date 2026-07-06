"""Tests del endpoint de interés en categorías en desarrollo (D50)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.interest.deps import get_repository
from ethos_api.interest.repository import InMemoryInterestRepository
from ethos_api.main import app
from tests.helpers import auth_headers


@pytest.fixture
def client(jwt_secret: str) -> Iterator[tuple[TestClient, InMemoryInterestRepository]]:
    repo = InMemoryInterestRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client, repo
    app.dependency_overrides.clear()


def test_registra_interes_anonimo(
    client: tuple[TestClient, InMemoryInterestRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"category": "places", "email": "ana@example.com"}
    respuesta = test_client.post("/category-interest", json=cuerpo)

    assert respuesta.status_code == 204
    registros = repo.list_for_category("places")
    assert len(registros) == 1
    assert registros[0].email == "ana@example.com"
    assert registros[0].user_id is None


def test_asocia_user_id_con_sesion(
    client: tuple[TestClient, InMemoryInterestRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"category": "food", "email": "leo@example.com"}
    respuesta = test_client.post("/category-interest", json=cuerpo, headers=auth_headers("user-9"))

    assert respuesta.status_code == 204
    registros = repo.list_for_category("food")
    assert registros[0].user_id == "user-9"


def test_registrarse_dos_veces_no_duplica(
    client: tuple[TestClient, InMemoryInterestRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"category": "board", "email": "sam@example.com"}
    test_client.post("/category-interest", json=cuerpo)
    test_client.post("/category-interest", json=cuerpo)

    assert len(repo.list_for_category("board")) == 1


def test_categoria_activa_rechazada(
    client: tuple[TestClient, InMemoryInterestRepository],
) -> None:
    test_client, _ = client
    cuerpo = {"category": "games", "email": "ana@example.com"}
    respuesta = test_client.post("/category-interest", json=cuerpo)
    assert respuesta.status_code == 422


def test_correo_invalido_rechazado(
    client: tuple[TestClient, InMemoryInterestRepository],
) -> None:
    test_client, _ = client
    cuerpo = {"category": "places", "email": "no-es-correo"}
    respuesta = test_client.post("/category-interest", json=cuerpo)
    assert respuesta.status_code == 422


def test_token_invalido_se_ignora_no_bloquea(
    client: tuple[TestClient, InMemoryInterestRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"category": "places", "email": "ana@example.com"}
    headers = {"Authorization": "Bearer token-basura"}
    respuesta = test_client.post("/category-interest", json=cuerpo, headers=headers)

    assert respuesta.status_code == 204
    assert repo.list_for_category("places")[0].user_id is None
