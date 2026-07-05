"""Tests de los endpoints del slice de música."""

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
from ethos_api.music.deps import get_event_store, get_listenbrainz_client
from ethos_api.music.store import InMemoryEventStore
from tests.helpers import auth_headers
from tests.music.helpers import FakeListenBrainzApi


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> Iterator[tuple[TestClient, InMemoryEventStore]]:
    monkeypatch.setattr(
        settings, "encryption_key", SecretStr(Fernet.generate_key().decode())
    )
    store = InMemoryEventStore()
    repo = InMemoryCredentialRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_event_store] = lambda: store
    app.dependency_overrides[get_listenbrainz_client] = FakeListenBrainzApi
    with TestClient(app) as test_client:
        yield test_client, store
    app.dependency_overrides.clear()


def _connect(test_client: TestClient, user: str = "user-1") -> None:
    respuesta = test_client.post(
        "/sources/listenbrainz",
        json={"user_name": "oyente"},
        headers=auth_headers(user),
    )
    assert respuesta.status_code == 201


def test_conectar_guarda_username_y_refresca(
    client: tuple[TestClient, InMemoryEventStore],
) -> None:
    test_client, _ = client
    _connect(test_client)
    estado = test_client.get("/sources/music", headers=auth_headers()).json()
    assert estado["state"] == "fresh"
    assert estado["summary"]["scrobbles_total"] == 3


def test_refresh_sin_conectar_da_404(
    client: tuple[TestClient, InMemoryEventStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post("/sources/listenbrainz/refresh", headers=auth_headers())
    assert respuesta.status_code == 404


def test_estado_vacio_sin_summary(
    client: tuple[TestClient, InMemoryEventStore],
) -> None:
    test_client, _ = client
    estado = test_client.get("/sources/music", headers=auth_headers("nadie")).json()
    assert estado["state"] == "never"
    assert estado["summary"] is None


def test_descarga_de_contexto_de_musica(
    client: tuple[TestClient, InMemoryEventStore],
) -> None:
    test_client, _ = client
    _connect(test_client)
    respuesta = test_client.get("/context/music", headers=auth_headers())
    assert respuesta.status_code == 200
    assert (
        respuesta.headers["content-disposition"]
        == 'attachment; filename="music.context.json"'
    )
    contexto = respuesta.json()
    assert contexto["namespace"] == "music.*"
    assert contexto["provider"] == "listenbrainz"


def test_los_listens_no_se_cruzan_entre_usuarios(
    client: tuple[TestClient, InMemoryEventStore],
) -> None:
    test_client, _ = client
    _connect(test_client, "user-1")
    ajeno = test_client.get("/sources/music", headers=auth_headers("user-2")).json()
    assert ajeno["state"] == "never"
