"""Tests del cliente y el conector de Trakt (sin red, con MockTransport)."""

from __future__ import annotations

import httpx
import pytest

from ethos_api.connectors.trakt.client import TraktApiClient, TraktApiError
from ethos_api.connectors.trakt.connector import TraktConnector, TraktRawData
from ethos_api.schema import Category, ItemStatus
from tests.film.helpers import SAMPLE_MOVIES, SAMPLE_SHOWS, SAMPLE_STATS


def _client(status_code: int = 200) -> tuple[TraktApiClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if status_code != 200:
            return httpx.Response(status_code, json={"error": "nope"})
        if request.url.path.endswith("/stats"):
            return httpx.Response(200, json=SAMPLE_STATS)
        if request.url.path.endswith("/watched/movies"):
            return httpx.Response(200, json=SAMPLE_MOVIES)
        return httpx.Response(200, json=SAMPLE_SHOWS)

    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.trakt.tv"
    )
    return TraktApiClient("client-id", client=http), requests


def test_get_watched_movies_parsea() -> None:
    client, requests = _client()
    data = client.get_watched_movies("cinefilo")
    assert data[0]["movie"]["title"] == "Inception"
    assert "/users/cinefilo/watched/movies" in requests[0].url.path


def test_get_watched_shows_parsea() -> None:
    client, _ = _client()
    data = client.get_watched_shows("cinefilo")
    assert data[0]["show"]["title"] == "Breaking Bad"


def test_get_user_stats_parsea() -> None:
    client, _ = _client()
    data = client.get_user_stats("cinefilo")
    assert data["movies"]["watched"] == 2


def test_error_lleva_status_code() -> None:
    client, _ = _client(status_code=404)
    with pytest.raises(TraktApiError) as exc:
        client.get_user_stats("cinefilo")
    assert exc.value.status_code == 404


def test_normaliza_peliculas_y_series() -> None:
    raw = TraktRawData(
        watched_movies=SAMPLE_MOVIES, watched_shows=SAMPLE_SHOWS, stats=SAMPLE_STATS
    )
    items = TraktConnector().normalize(raw)

    assert len(items) == 3  # 2 películas + 1 serie
    movie = items[0]
    assert movie.category is Category.film
    assert movie.status is ItemStatus.consumed
    assert movie.work.title == "Inception"
    assert movie.work.year == 2010
    assert movie.work.external_ids["imdb"] == "tt1375666"
    assert movie.work.extra["media_type"] == "movie"
    assert movie.engagement["plays"] == 3

    show = items[-1]
    assert show.work.extra["media_type"] == "show"
    # Episodios vistos = suma de episodios de las temporadas (3 + 2).
    assert show.engagement["episodes_watched"] == 5


def test_stats_extrae_agregados() -> None:
    raw = TraktRawData(stats=SAMPLE_STATS)
    stats = TraktConnector.stats(raw)
    assert stats.movies_watched == 2
    assert stats.movies_minutes == 260
    assert stats.episodes_watched == 5
    assert stats.episodes_minutes == 2790


def test_identidad_del_conector() -> None:
    assert TraktConnector.id == "trakt"
    assert TraktConnector.category is Category.film
