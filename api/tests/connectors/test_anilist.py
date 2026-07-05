"""Tests del cliente y el conector de AniList."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from ethos_api.connectors.anilist.client import AniListApiClient, AniListApiError
from ethos_api.connectors.anilist.connector import AniListConnector, AniListRawData
from ethos_api.schema import Category, ItemStatus
from tests.anime.helpers import SAMPLE_MEDIA_LISTS


def _client_with(handler: httpx.MockTransport) -> AniListApiClient:
    http = httpx.Client(base_url="https://graphql.anilist.co", transport=handler)
    return AniListApiClient(client=http, min_interval_seconds=0)


def test_get_media_lists_devuelve_data() -> None:
    captured: dict[str, Any] = {}

    def responder(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"data": SAMPLE_MEDIA_LISTS})

    client = _client_with(httpx.MockTransport(responder))
    data = client.get_media_lists("otaku")
    assert data == SAMPLE_MEDIA_LISTS
    assert captured["variables"] == {"userName": "otaku"}
    assert "MediaListCollection" in captured["query"]


def test_status_no_200_lanza_error_con_codigo() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={})

    client = _client_with(httpx.MockTransport(responder))
    with pytest.raises(AniListApiError) as excinfo:
        client.get_media_lists("otaku")
    assert excinfo.value.status_code == 429


def test_errores_graphql_embebidos_propagan_status() -> None:
    # AniList responde 200/404 con errores embebidos para usuarios privados.
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {"anime": None, "manga": None},
                "errors": [{"message": "Private User", "status": 404}],
            },
        )

    client = _client_with(httpx.MockTransport(responder))
    with pytest.raises(AniListApiError) as excinfo:
        client.get_media_lists("privado")
    assert excinfo.value.status_code == 404


def test_respuesta_no_json_esperado_lanza_error() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[1, 2])

    client = _client_with(httpx.MockTransport(responder))
    with pytest.raises(AniListApiError):
        client.get_media_lists("otaku")


def _raw() -> AniListRawData:
    return AniListRawData(
        anime_lists=SAMPLE_MEDIA_LISTS["anime"]["lists"],
        manga_lists=SAMPLE_MEDIA_LISTS["manga"]["lists"],
    )


def test_normaliza_anime_y_manga_con_dedupe() -> None:
    items = AniListConnector().normalize(_raw())
    # 2 animes (la lista personalizada duplicada se ignora) + 2 mangas.
    assert len(items) == 4
    assert all(i.category is Category.anime for i in items)

    aot = next(i for i in items if i.work.title == "Shingeki no Kyojin")
    assert aot.status is ItemStatus.consumed
    assert aot.rating_normalized == 90
    assert aot.engagement["episodes_progress"] == 26
    assert aot.work.external_ids == {"anilist": "16498"}
    assert aot.work.extra["media_type"] == "anime"

    one_piece = next(i for i in items if i.work.title == "One Piece")
    assert one_piece.status is ItemStatus.in_progress
    # Score 0 en AniList significa "sin puntuar".
    assert one_piece.rating_normalized is None

    monster = next(i for i in items if i.work.title == "Monster")
    assert monster.status is ItemStatus.wishlist
    assert monster.work.extra["media_type"] == "manga"


def test_entradas_sin_titulo_se_descartan() -> None:
    raw = AniListRawData(
        anime_lists=[
            {
                "isCustomList": False,
                "entries": [{"status": "COMPLETED", "media": {"id": 1, "title": {}}}],
            }
        ]
    )
    assert AniListConnector().normalize(raw) == []
