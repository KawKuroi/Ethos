"""Tests del cliente y el conector de Kitsu."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ethos_api.connectors.kitsu.client import KitsuApiError, KitsuClient
from ethos_api.connectors.kitsu.connector import KitsuConnector, KitsuRawData
from ethos_api.schema import Category, ItemStatus

ANIME_LIBRARY: dict[str, Any] = {
    "data": [
        {
            "attributes": {
                "status": "completed",
                "progress": 25,
                "ratingTwenty": 18,
                "reconsumeCount": 1,
                "updatedAt": "2026-07-01T10:20:30.000Z",
            },
            "relationships": {"anime": {"data": {"id": "7442", "type": "anime"}}},
        },
        {
            "attributes": {"status": "planned", "progress": 0, "ratingTwenty": None},
            "relationships": {"anime": {"data": {"id": "12", "type": "anime"}}},
        },
        {
            # Sin obra incluida: se descarta.
            "attributes": {"status": "completed", "progress": 1},
            "relationships": {"anime": {"data": {"id": "999", "type": "anime"}}},
        },
    ],
    "included": [
        {
            "id": "7442",
            "type": "anime",
            "attributes": {
                "canonicalTitle": "Attack on Titan",
                "subtype": "TV",
            },
        },
        {
            "id": "12",
            "type": "anime",
            "attributes": {"canonicalTitle": "One Piece", "subtype": "TV"},
        },
    ],
}

MANGA_LIBRARY: dict[str, Any] = {
    "data": [
        {
            "attributes": {"status": "current", "progress": 380, "ratingTwenty": 20},
            "relationships": {"manga": {"data": {"id": "22", "type": "manga"}}},
        }
    ],
    "included": [
        {
            "id": "22",
            "type": "manga",
            "attributes": {"canonicalTitle": "Berserk", "subtype": "manga"},
        }
    ],
}


def _client(
    respuestas: list[dict[str, Any]], status_code: int = 200
) -> tuple[KitsuClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []
    paginas = iter(respuestas)

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if status_code != 200:
            return httpx.Response(status_code, json={})
        return httpx.Response(200, json=next(paginas))

    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://kitsu.io/api/edge"
    )
    return KitsuClient(client=http), requests


def test_find_user_id_resuelve_por_nombre() -> None:
    client, requests = _client([{"data": [{"id": "42"}]}])
    assert client.find_user_id("otaku") == "42"
    assert "filter%5Bname%5D=otaku" in str(requests[0].url)


def test_usuario_inexistente_lanza_404() -> None:
    client, _ = _client([{"data": []}])
    with pytest.raises(KitsuApiError) as info:
        client.find_user_id("nadie")
    assert info.value.status_code == 404


def test_get_library_concatena_paginas() -> None:
    pagina_1 = {
        "data": ANIME_LIBRARY["data"][:2],
        "included": ANIME_LIBRARY["included"][:1],
        "links": {"next": "https://kitsu.io/api/edge/library-entries?page%5Boffset%5D=2"},
    }
    pagina_2 = {
        "data": ANIME_LIBRARY["data"][2:],
        "included": ANIME_LIBRARY["included"][1:],
        "links": {},
    }
    client, requests = _client([pagina_1, pagina_2])
    library = client.get_library("42", "anime")
    assert len(library["data"]) == 3
    assert len(library["included"]) == 2
    assert len(requests) == 2


def test_normaliza_library_entries_al_contrato() -> None:
    raw = KitsuRawData(anime_library=ANIME_LIBRARY, manga_library=MANGA_LIBRARY)
    items = KitsuConnector().normalize(raw)

    # La entrada sin obra incluida se descarta: 2 animes + 1 manga.
    assert len(items) == 3
    aot = items[0]
    assert aot.category is Category.anime
    assert aot.source == "kitsu"
    assert aot.status is ItemStatus.consumed
    assert aot.rating_normalized == 90  # ratingTwenty 18 → 0-100
    assert aot.engagement == {"episodes_progress": 25, "repeat": 1}
    assert aot.work.external_ids == {"kitsu": "7442"}
    assert aot.work.extra["media_type"] == "anime"

    berserk = items[2]
    assert berserk.work.title == "Berserk"
    assert berserk.engagement["chapters_read"] == 380
    assert berserk.status is ItemStatus.in_progress
