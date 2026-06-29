"""Tests del cliente de la Steam Web API (sin red, con MockTransport)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from ethos_api.connectors.steam.client import SteamApiClient, SteamApiError

_FIXTURES = Path(__file__).parent.parent / "fixtures"


def _load(nombre: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / nombre).read_text(encoding="utf-8"))


def _client_con_respuesta(payload: dict[str, Any], status_code: int = 200) -> SteamApiClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload)

    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport, base_url="https://api.steampowered.com")
    return SteamApiClient(api_key="test-key", client=http)


def test_get_owned_games_parsea() -> None:
    client = _client_con_respuesta(_load("steam_owned_games.json"))
    data = client.get_owned_games("123")
    assert data["response"]["game_count"] == 2


def test_get_player_summary_parsea() -> None:
    client = _client_con_respuesta(_load("steam_player_summary.json"))
    data = client.get_player_summary("123")
    assert data["response"]["players"][0]["steamid"] == "76561197960287930"


def test_error_en_no_200() -> None:
    client = _client_con_respuesta({}, status_code=403)
    with pytest.raises(SteamApiError):
        client.get_owned_games("123")
