"""Tests del cliente y el conector de MyAnimeList."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ethos_api.connectors.mal.client import MalApiError, MalClient
from ethos_api.connectors.mal.connector import MalConnector, MalRawData
from ethos_api.schema import Category, ItemStatus

ANIME_ENTRIES: list[dict[str, Any]] = [
    {
        "node": {"id": 16498, "title": "Shingeki no Kyojin", "media_type": "tv"},
        "list_status": {
            "status": "completed",
            "score": 9,
            "num_episodes_watched": 25,
            "num_times_rewatched": 1,
            "updated_at": "2026-07-01T10:20:30+00:00",
        },
    },
    {
        "node": {"id": 21, "title": "One Piece", "media_type": "tv"},
        "list_status": {
            "status": "watching",
            "score": 0,
            "num_episodes_watched": 8,
        },
    },
    {
        # Duplicado del primero: se ignora.
        "node": {"id": 16498, "title": "Shingeki no Kyojin"},
        "list_status": {"status": "completed", "score": 9},
    },
]

MANGA_ENTRIES: list[dict[str, Any]] = [
    {
        "node": {"id": 2, "title": "Berserk", "media_type": "manga"},
        "list_status": {
            "status": "reading",
            "score": 10,
            "num_chapters_read": 380,
        },
    },
    {
        "node": {"id": 1, "title": "Monster"},
        "list_status": {"status": "plan_to_read", "score": 0},
    },
]


def _client(
    pages: list[dict[str, Any]], status_code: int = 200
) -> tuple[MalClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []
    respuestas = iter(pages)

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if status_code != 200:
            return httpx.Response(status_code, json={})
        return httpx.Response(200, json=next(respuestas))

    http = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.myanimelist.net",
        headers={"X-MAL-CLIENT-ID": "client-id"},
    )
    return MalClient("client-id", client=http), requests


def test_get_anime_list_sigue_la_paginacion() -> None:
    client, requests = _client(
        [
            {
                "data": ANIME_ENTRIES[:2],
                "paging": {"next": "https://api.myanimelist.net/v2/users/u/animelist?offset=2"},
            },
            {"data": ANIME_ENTRIES[2:], "paging": {}},
        ]
    )
    entries = client.get_anime_list("otaku")
    assert len(entries) == 3
    assert len(requests) == 2
    assert "/v2/users/otaku/animelist" in requests[0].url.path


def test_lista_privada_lanza_error_con_codigo() -> None:
    client, _ = _client([], status_code=403)
    with pytest.raises(MalApiError) as info:
        client.get_anime_list("privado")
    assert info.value.status_code == 403


def test_normaliza_listas_al_contrato() -> None:
    raw = MalRawData(anime_entries=ANIME_ENTRIES, manga_entries=MANGA_ENTRIES)
    items = MalConnector().normalize(raw)

    # Dedupe: 2 animes + 2 mangas.
    assert len(items) == 4
    aot = items[0]
    assert aot.category is Category.anime
    assert aot.source == "mal"
    assert aot.status is ItemStatus.consumed
    assert aot.rating_normalized == 90  # score 9 → 0-100
    assert aot.engagement == {"episodes_progress": 25, "repeat": 1}
    assert aot.work.external_ids == {"mal": "16498"}
    assert aot.work.extra["media_type"] == "anime"
    assert aot.work.extra["format"] == "TV"
    assert isinstance(aot.work.extra["updated_at"], int)

    berserk = items[2]
    assert berserk.work.extra["media_type"] == "manga"
    assert berserk.engagement["chapters_read"] == 380
    assert berserk.status is ItemStatus.in_progress

    monster = items[3]
    assert monster.status is ItemStatus.wishlist
    assert monster.rating_normalized is None
