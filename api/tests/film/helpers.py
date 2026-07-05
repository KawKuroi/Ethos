"""Helpers del slice de Cine y TV: datos de muestra y fake del cliente de Trakt."""

from __future__ import annotations

from typing import Any

from ethos_api.connectors.trakt.client import TraktApiError

# Respuestas de muestra de Trakt (misma forma que la API real).
SAMPLE_MOVIES: list[dict[str, Any]] = [
    {
        "plays": 3,
        "last_watched_at": "2026-06-30T20:00:00.000Z",
        "movie": {
            "title": "Inception",
            "year": 2010,
            "ids": {
                "trakt": 1,
                "slug": "inception-2010",
                "imdb": "tt1375666",
                "tmdb": 27205,
            },
        },
    },
    {
        "plays": 1,
        "last_watched_at": "2026-05-01T18:00:00.000Z",
        "movie": {
            "title": "Arrival",
            "year": 2016,
            "ids": {
                "trakt": 2,
                "slug": "arrival-2016",
                "imdb": "tt2543164",
                "tmdb": 329865,
            },
        },
    },
]

SAMPLE_SHOWS: list[dict[str, Any]] = [
    {
        "plays": 62,
        "last_watched_at": "2026-07-01T22:00:00.000Z",
        "show": {
            "title": "Breaking Bad",
            "year": 2008,
            "ids": {
                "trakt": 1,
                "slug": "breaking-bad",
                "imdb": "tt0903747",
                "tmdb": 1396,
            },
        },
        "seasons": [
            {"number": 1, "episodes": [{"number": 1}, {"number": 2}, {"number": 3}]},
            {"number": 2, "episodes": [{"number": 1}, {"number": 2}]},
        ],
    },
]

SAMPLE_STATS: dict[str, Any] = {
    "movies": {"plays": 4, "watched": 2, "minutes": 260},
    "shows": {"watched": 1, "collected": 0},
    "seasons": {"ratings": 0},
    "episodes": {"plays": 62, "watched": 5, "minutes": 2790},
}


class FakeTraktApi:
    """Cliente falso de Trakt para los tests del servicio y los endpoints."""

    def __init__(self, *, fail: bool = False, status_code: int | None = None) -> None:
        self.fail = fail
        self.status_code = status_code
        self.calls: list[str] = []

    def _maybe_fail(self) -> None:
        if self.status_code is not None:
            raise TraktApiError("Trakt error", status_code=self.status_code)
        if self.fail:
            raise RuntimeError("Trakt respondió 500")

    def get_user_stats(self, user_name: str) -> dict[str, Any]:
        self.calls.append("stats")
        self._maybe_fail()
        return SAMPLE_STATS

    def get_watched_movies(self, user_name: str) -> list[dict[str, Any]]:
        self.calls.append("movies")
        self._maybe_fail()
        return SAMPLE_MOVIES

    def get_watched_shows(self, user_name: str) -> list[dict[str, Any]]:
        self.calls.append("shows")
        self._maybe_fail()
        return SAMPLE_SHOWS
