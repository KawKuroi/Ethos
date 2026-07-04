"""Tests de los endpoints del slice de juegos (fuentes + contexto)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from pydantic import SecretStr

from ethos_api.config import settings
from ethos_api.credentials.deps import get_repository
from ethos_api.credentials.repository import InMemoryCredentialRepository
from ethos_api.games.deps import get_games_store, get_openid_verifier, get_steam_client
from ethos_api.games.store import InMemoryGamesStore
from ethos_api.main import app
from tests.games.helpers import FakeSteamApi
from tests.helpers import auth_headers

_STEAMID = "76561197960287930"


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch, jwt_secret: str
) -> Iterator[tuple[TestClient, InMemoryGamesStore]]:
    monkeypatch.setattr(
        settings, "encryption_key", SecretStr(Fernet.generate_key().decode())
    )
    store = InMemoryGamesStore()
    repo = InMemoryCredentialRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_games_store] = lambda: store
    app.dependency_overrides[get_steam_client] = FakeSteamApi
    app.dependency_overrides[get_openid_verifier] = lambda: (lambda params: _STEAMID)
    with TestClient(app) as test_client:
        yield test_client, store
    app.dependency_overrides.clear()


def _connect(test_client: TestClient, user: str = "user-1") -> None:
    respuesta = test_client.post(
        "/sources/steam",
        json={"params": {"openid.mode": "id_res"}},
        headers=auth_headers(user),
    )
    assert respuesta.status_code == 201


def test_conectar_steam_guarda_credencial_y_refresca(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _store = client
    _connect(test_client)

    # TestClient ejecuta las BackgroundTasks al cerrar la respuesta: el primer
    # refresco ya corrió.
    estado = test_client.get("/sources/games", headers=auth_headers()).json()
    assert estado["state"] == "fresh"
    assert estado["persona_name"] == "Jugador"
    assert estado["summary"]["games"] == 2
    assert estado["summary"]["wishlisted"] == 3


def test_refresh_sin_credencial_da_404(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post("/sources/steam/refresh", headers=auth_headers())
    assert respuesta.status_code == 404


def test_refresh_encolado_da_202(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    _connect(test_client)
    respuesta = test_client.post("/sources/steam/refresh", headers=auth_headers())
    assert respuesta.status_code == 202
    assert respuesta.json() == {"status": "queued"}


def test_contexto_sin_sincronizar_da_404(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.get("/context/games", headers=auth_headers())
    assert respuesta.status_code == 404


def test_descarga_de_contexto_d24(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    _connect(test_client)

    respuesta = test_client.get("/context/games", headers=auth_headers())
    assert respuesta.status_code == 200
    assert (
        respuesta.headers["content-disposition"]
        == 'attachment; filename="games.context.json"'
    )
    contexto = respuesta.json()
    assert contexto["namespace"] == "games.*"
    assert contexto["summary"]["games"] == 2
    assert contexto["wishlist"]["count"] == 3


def test_los_datos_no_se_cruzan_entre_usuarios(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    _connect(test_client, "user-1")

    ajeno = test_client.get("/sources/games", headers=auth_headers("user-2")).json()
    assert ajeno["state"] == "never"
    assert ajeno["summary"] is None


def test_login_de_steam_devuelve_url_de_openid(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    return_to = "https://ethos-steel.vercel.app/app/steam/return"
    respuesta = test_client.get(
        "/sources/steam/login",
        params={"return_to": return_to},
        headers=auth_headers(),
    )
    assert respuesta.status_code == 200
    url = respuesta.json()["url"]
    assert url.startswith("https://steamcommunity.com/openid/login")
    assert "checkid_setup" in url


def test_login_rechaza_return_to_relativo(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.get(
        "/sources/steam/login", params={"return_to": "/app"}, headers=auth_headers()
    )
    assert respuesta.status_code == 400


def test_openid_invalido_da_400(
    client: tuple[TestClient, InMemoryGamesStore],
) -> None:
    from ethos_api.connectors.steam.openid import SteamOpenIdError

    def rechaza(params: dict[str, str]) -> str:
        raise SteamOpenIdError("firma inválida")

    app.dependency_overrides[get_openid_verifier] = lambda: rechaza
    test_client, _ = client
    respuesta = test_client.post(
        "/sources/steam", json={"params": {}}, headers=auth_headers()
    )
    assert respuesta.status_code == 400
