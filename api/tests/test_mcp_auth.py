"""Tests de la auth del MCP (D22) y de las tools de datos (D28)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.games.store import InMemoryGamesStore
from ethos_api.main import app
from ethos_api.mcp_auth import InMemoryMcpTokenStore, user_from_authorization
from ethos_api.mcp_server import (
    games_summary_payload,
    games_top_payload,
    profile_search_payload,
)
from tests.games.helpers import FakeSteamApi
from tests.helpers import auth_headers


def test_emitir_y_resolver_token() -> None:
    store = InMemoryMcpTokenStore()
    token = store.issue("user-1")
    assert token.startswith("eth_live_")
    assert store.resolve(token) == "user-1"


def test_emitir_de_nuevo_rota_el_anterior() -> None:
    store = InMemoryMcpTokenStore()
    primero = store.issue("user-1")
    segundo = store.issue("user-1")
    assert store.resolve(primero) is None
    assert store.resolve(segundo) == "user-1"


def test_resolver_rechaza_tokens_ajenos() -> None:
    store = InMemoryMcpTokenStore()
    store.issue("user-1")
    assert store.resolve("eth_live_invento") is None
    assert store.resolve("otro-esquema") is None


def test_user_from_authorization() -> None:
    store = InMemoryMcpTokenStore()
    token = store.issue("user-1")
    assert user_from_authorization(f"Bearer {token}", store) == "user-1"
    assert user_from_authorization(token, store) is None
    assert user_from_authorization(None, store) is None


@pytest.fixture
def api_client(jwt_secret: str) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_endpoint_emite_token_con_sesion(api_client: TestClient) -> None:
    respuesta = api_client.post("/mcp-token", headers=auth_headers())
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["token"].startswith("eth_live_")
    assert datos["endpoint"].endswith("/mcp/")


def test_endpoint_requiere_sesion(api_client: TestClient) -> None:
    assert api_client.post("/mcp-token").status_code == 401


def _store_poblado(user: str = "user-1") -> InMemoryGamesStore:
    from ethos_api.games.service import refresh_user_games

    store = InMemoryGamesStore()
    refresh_user_games(user, "765", FakeSteamApi(), store)
    return store


def test_payload_del_resumen_reporta_kb() -> None:
    store = _store_poblado()
    payload = games_summary_payload("user-1", store)
    assert payload["games"] == 2
    kb_served, kb_total = payload["kb_served"], payload["kb_total"]
    assert isinstance(kb_served, float) and kb_served > 0
    assert isinstance(kb_total, float) and kb_total > 0


def test_payload_del_top_respeta_limit() -> None:
    store = _store_poblado()
    payload = games_top_payload("user-1", store, limit=1)
    top = payload["top_by_hours"]
    assert isinstance(top, list)
    assert len(top) == 1
    assert top[0]["title"] == "Dota 2"


def test_profile_search_encuentra_y_degrada() -> None:
    store = _store_poblado()

    con_match = profile_search_payload("user-1", store, "fortress")
    assert con_match["matched"] is True

    sin_match = profile_search_payload("user-1", store, "zelda")
    assert sin_match["matched"] is False
    assert "hint" in sin_match


@pytest.mark.anyio
async def test_tools_de_datos_exigen_token() -> None:
    """En transporte in-memory no hay headers: la tool debe rechazar (D22)."""
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="No autenticado"):
            await client.call_tool("games.summary", {})


@pytest.mark.anyio
async def test_ping_sigue_abierto() -> None:
    from fastmcp import Client

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        result = await client.call_tool("ping", {})
        assert result.data == "pong"
