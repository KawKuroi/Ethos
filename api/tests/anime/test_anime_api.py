"""Tests de los endpoints del slice de Anime y manga."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from pydantic import SecretStr

from ethos_api.anime.deps import get_anilist_client, get_anime_store
from ethos_api.anime.store import InMemoryAnimeStore
from ethos_api.config import settings
from ethos_api.credentials.deps import get_repository
from ethos_api.credentials.repository import InMemoryCredentialRepository
from ethos_api.main import app
from tests.anime.helpers import FakeAniListApi
from tests.helpers import auth_headers


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> Iterator[tuple[TestClient, InMemoryAnimeStore]]:
    monkeypatch.setattr(
        settings, "encryption_key", SecretStr(Fernet.generate_key().decode())
    )
    store = InMemoryAnimeStore()
    repo = InMemoryCredentialRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_anime_store] = lambda: store
    app.dependency_overrides[get_anilist_client] = FakeAniListApi
    with TestClient(app) as test_client:
        yield test_client, store
    app.dependency_overrides.clear()


def _connect(test_client: TestClient, user: str = "user-1") -> None:
    respuesta = test_client.post(
        "/sources/anilist",
        json={"user_name": "otaku"},
        headers=auth_headers(user),
    )
    assert respuesta.status_code == 201


def test_conectar_guarda_username_y_refresca(
    client: tuple[TestClient, InMemoryAnimeStore],
) -> None:
    test_client, _ = client
    _connect(test_client)
    estado = test_client.get("/sources/anime", headers=auth_headers()).json()
    assert estado["state"] == "fresh"
    assert estado["summary"]["anime_watched"] == 1
    assert estado["summary"]["chapters_read"] == 205


def test_refresh_sin_conectar_da_404(
    client: tuple[TestClient, InMemoryAnimeStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post("/sources/anilist/refresh", headers=auth_headers())
    assert respuesta.status_code == 404


def test_estado_vacio_sin_summary(
    client: tuple[TestClient, InMemoryAnimeStore],
) -> None:
    test_client, _ = client
    estado = test_client.get("/sources/anime", headers=auth_headers("nadie")).json()
    assert estado["state"] == "never"
    assert estado["summary"] is None


def test_descarga_de_contexto_de_anime(
    client: tuple[TestClient, InMemoryAnimeStore],
) -> None:
    test_client, _ = client
    _connect(test_client)
    respuesta = test_client.get("/context/anime", headers=auth_headers())
    assert respuesta.status_code == 200
    assert (
        respuesta.headers["content-disposition"]
        == 'attachment; filename="anime.context.json"'
    )
    contexto = respuesta.json()
    assert contexto["namespace"] == "anime.*"
    assert contexto["provider"] == "anilist"


def test_contexto_sin_datos_da_404(
    client: tuple[TestClient, InMemoryAnimeStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.get("/context/anime", headers=auth_headers("nadie"))
    assert respuesta.status_code == 404


def test_los_datos_no_se_cruzan_entre_usuarios(
    client: tuple[TestClient, InMemoryAnimeStore],
) -> None:
    test_client, _ = client
    _connect(test_client, "user-1")
    ajeno = test_client.get("/sources/anime", headers=auth_headers("user-2")).json()
    assert ajeno["state"] == "never"
