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


def test_get_recently_played_parsea() -> None:
    client = _client_con_respuesta(_load("steam_recently_played.json"))
    data = client.get_recently_played("123")
    assert data["response"]["games"][0]["appid"] == 440


def test_get_wishlist_parsea() -> None:
    client = _client_con_respuesta(_load("steam_wishlist.json"))
    data = client.get_wishlist("123")
    assert data["response"]["items"][0]["appid"] == 1145360


def test_get_player_achievements_parsea() -> None:
    client = _client_con_respuesta(_load("steam_achievements.json"))
    data = client.get_player_achievements("123", 440)
    assert data["playerstats"]["gameName"] == "Team Fortress 2"


def test_error_en_no_200() -> None:
    client = _client_con_respuesta({}, status_code=403)
    with pytest.raises(SteamApiError):
        client.get_owned_games("123")


def test_error_en_respuesta_no_dict() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[1, 2, 3])

    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.steampowered.com"
    )
    client = SteamApiClient(api_key="test-key", client=http)
    with pytest.raises(SteamApiError):
        client.get_owned_games("123")


def test_throttle_espera_entre_llamadas_consecutivas() -> None:
    # Reloj falso: avanza 0,2 s por lectura; el intervalo mínimo es 1 s, así
    # que la segunda llamada debe dormir el tiempo restante (sin dormir real).
    ticks = iter(x * 0.2 for x in range(100))
    esperas: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": {}})

    http = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.steampowered.com",
    )
    client = SteamApiClient(
        api_key="test-key",
        client=http,
        min_interval_seconds=1.0,
        clock=lambda: next(ticks),
        sleep=esperas.append,
    )

    client.get_owned_games("123")   # primera llamada: sin espera
    client.get_owned_games("123")   # segunda: debe respetar el intervalo
    assert len(esperas) == 1
    assert 0 < esperas[0] <= 1.0
