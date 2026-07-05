"""Tests del cliente y el conector de ListenBrainz."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from ethos_api.connectors.listenbrainz.client import (
    ListenBrainzApiError,
    ListenBrainzClient,
)
from ethos_api.connectors.listenbrainz.connector import (
    ListenBrainzConnector,
    ListenBrainzRawData,
)
from ethos_api.schema import Category

_FIXTURES = Path(__file__).parent.parent / "fixtures"


def _load(nombre: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / nombre).read_text(encoding="utf-8"))


def _client(
    payload: dict[str, Any], status_code: int = 200
) -> tuple[ListenBrainzClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status_code, json=payload)

    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.listenbrainz.org"
    )
    return ListenBrainzClient(client=http), requests


def test_get_listens_pasa_min_ts() -> None:
    client, requests = _client(_load("listenbrainz_listens.json"))
    data = client.get_listens("oyente", min_ts=1709999999)
    assert data["payload"]["count"] == 4
    assert "min_ts=1709999999" in str(requests[0].url)
    assert "/1/user/oyente/listens" in requests[0].url.path


def test_get_listens_error() -> None:
    client, _ = _client({}, status_code=404)
    with pytest.raises(ListenBrainzApiError):
        client.get_listens("oyente")


def test_normaliza_listens_a_eventos() -> None:
    raw = ListenBrainzRawData(listens=_load("listenbrainz_listens.json"))
    events = ListenBrainzConnector().normalize(raw)

    # El listen sin artista/track se descarta; quedan 3.
    assert len(events) == 3
    primero = events[0]
    assert primero.category is Category.music
    assert primero.payload["artist"] == "Alvvays"
    assert primero.payload["track"] == "Belinda Says"
    assert primero.payload["release"] == "Blue Rev"
    assert primero.occurred_at == datetime.fromtimestamp(1710000300, tz=UTC)


def test_latest_listened_at() -> None:
    raw = ListenBrainzRawData(listens=_load("listenbrainz_listens.json"))
    assert ListenBrainzConnector.latest_listened_at(raw) == 1710000300


def test_identidad_del_conector() -> None:
    assert ListenBrainzConnector.id == "listenbrainz"
    assert ListenBrainzConnector.category is Category.music
