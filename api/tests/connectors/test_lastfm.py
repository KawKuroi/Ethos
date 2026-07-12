"""Tests del cliente y el conector de Last.fm."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx
import pytest

from ethos_api.connectors.lastfm.client import LastfmApiError, LastfmClient
from ethos_api.connectors.lastfm.connector import LastfmConnector, LastfmRawData
from ethos_api.schema import Category

SAMPLE_PAGE: dict[str, Any] = {
    "recenttracks": {
        "track": [
            {
                # Track sonando ahora: sin fecha, se descarta.
                "name": "Now Playing",
                "artist": {"#text": "Alguien"},
                "album": {"#text": ""},
                "@attr": {"nowplaying": "true"},
            },
            {
                "name": "Belinda Says",
                "artist": {"#text": "Alvvays"},
                "album": {"#text": "Blue Rev"},
                "date": {"uts": "1710000300"},
            },
            {
                "name": "Archie, Marry Me",
                "artist": {"#text": "Alvvays"},
                "album": {"#text": ""},
                "date": {"uts": "1710000000"},
            },
            {
                # Sin artista: se descarta.
                "name": "Huerfana",
                "artist": {"#text": ""},
                "date": {"uts": "1709990000"},
            },
        ],
        "@attr": {"totalPages": "1", "page": "1"},
    }
}


def _client(
    payload: dict[str, Any], status_code: int = 200
) -> tuple[LastfmClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status_code, json=payload)

    http = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://ws.audioscrobbler.com",
    )
    return LastfmClient("clave-app", client=http), requests


def test_get_recent_tracks_pasa_from_y_api_key() -> None:
    client, requests = _client(SAMPLE_PAGE)
    data = client.get_recent_tracks("oyente", from_ts=1709999999)
    assert data["recenttracks"]["@attr"]["page"] == "1"
    url = str(requests[0].url)
    assert "from=1709999999" in url
    assert "api_key=clave-app" in url
    assert "user=oyente" in url


def test_error_http_lanza_lastfm_error() -> None:
    client, _ = _client({}, status_code=500)
    with pytest.raises(LastfmApiError):
        client.get_recent_tracks("oyente")


def test_error_embebido_usuario_no_encontrado() -> None:
    client, _ = _client({"error": 6, "message": "User not found"})
    with pytest.raises(LastfmApiError) as info:
        client.get_recent_tracks("nadie")
    assert info.value.status_code == 404


def test_normaliza_scrobbles_a_eventos() -> None:
    events = LastfmConnector().normalize(LastfmRawData(pages=[SAMPLE_PAGE]))
    # Fuera el "now playing" y el track sin artista; quedan 2.
    assert len(events) == 2
    primero = events[0]
    assert primero.category is Category.music
    assert primero.source == "lastfm"
    assert primero.payload["artist"] == "Alvvays"
    assert primero.payload["release"] == "Blue Rev"
    assert primero.occurred_at == datetime.fromtimestamp(1710000300, tz=UTC)
    # El segundo no trae release: la clave no viaja vacía.
    assert "release" not in events[1].payload


def test_normaliza_track_unico_como_objeto() -> None:
    # Con un solo scrobble la API devuelve un objeto en vez de una lista.
    page = {
        "recenttracks": {
            "track": {
                "name": "Solo",
                "artist": {"#text": "Alguien"},
                "date": {"uts": "1710000100"},
            }
        }
    }
    events = LastfmConnector().normalize(LastfmRawData(pages=[page]))
    assert len(events) == 1


def test_latest_scrobbled_at() -> None:
    assert LastfmConnector.latest_scrobbled_at(LastfmRawData(pages=[SAMPLE_PAGE])) == 1710000300
    assert LastfmConnector.latest_scrobbled_at(LastfmRawData(pages=[])) is None
