"""Tests de los endpoints de credenciales (con repositorio en memoria y JWT de prueba)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from pydantic import SecretStr

from ethos_api.config import settings
from ethos_api.credentials.deps import get_repository
from ethos_api.credentials.repository import InMemoryCredentialRepository
from ethos_api.main import app
from tests.helpers import auth_headers


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    jwt_secret: str,
) -> Iterator[tuple[TestClient, InMemoryCredentialRepository]]:
    monkeypatch.setattr(settings, "encryption_key", SecretStr(Fernet.generate_key().decode()))
    repo = InMemoryCredentialRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client, repo
    app.dependency_overrides.clear()


def test_conectar_guarda_cifrado_y_no_devuelve_token(
    client: tuple[TestClient, InMemoryCredentialRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"provider": "listenbrainz", "category": "music", "token": "secreto-123"}
    respuesta = test_client.post("/credentials", json=cuerpo, headers=auth_headers())

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["provider"] == "listenbrainz"
    assert "token" not in datos
    assert "encrypted_token" not in datos

    guardada = repo.get("user-1", "listenbrainz")
    assert guardada is not None
    assert guardada.encrypted_token != "secreto-123"


def test_listar_solo_lo_propio(
    client: tuple[TestClient, InMemoryCredentialRepository],
) -> None:
    test_client, _ = client
    cuerpo = {"provider": "listenbrainz", "category": "music", "token": "a"}
    test_client.post("/credentials", json=cuerpo, headers=auth_headers("user-1"))

    propios = test_client.get("/credentials", headers=auth_headers("user-1")).json()
    ajenos = test_client.get("/credentials", headers=auth_headers("user-2")).json()
    assert len(propios) == 1
    assert ajenos == []


def test_requiere_autenticacion(
    client: tuple[TestClient, InMemoryCredentialRepository],
) -> None:
    test_client, _ = client
    cuerpo = {"provider": "listenbrainz", "category": "music", "token": "a"}
    respuesta = test_client.post("/credentials", json=cuerpo)
    assert respuesta.status_code == 401


def test_desconectar(
    client: tuple[TestClient, InMemoryCredentialRepository],
) -> None:
    test_client, _ = client
    cuerpo = {"provider": "listenbrainz", "category": "music", "token": "a"}
    test_client.post("/credentials", json=cuerpo, headers=auth_headers())

    borrado = test_client.delete("/credentials/listenbrainz", headers=auth_headers())
    assert borrado.status_code == 204
    assert test_client.get("/credentials", headers=auth_headers()).json() == []


def test_desconectar_inexistente_da_404(
    client: tuple[TestClient, InMemoryCredentialRepository],
) -> None:
    test_client, _ = client
    respuesta = test_client.delete("/credentials/trakt", headers=auth_headers())
    assert respuesta.status_code == 404
