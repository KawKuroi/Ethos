"""Generador del resumen de Cine y TV desde los registros normalizados (D43)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ethos_api.connectors.trakt.connector import TraktStats
from ethos_api.schema import NormalizedItem


class TopMovie(BaseModel):
    """Entrada del top de películas por reproducciones."""

    title: str
    year: int | None = None
    plays: int


class TopShow(BaseModel):
    """Entrada del top de series por episodios vistos."""

    title: str
    episodes_watched: int


class RecentWatch(BaseModel):
    """Obra vista recientemente (película o serie)."""

    title: str
    media_type: str
    watched_at: datetime | None = None


class FilmSummary(BaseModel):
    """Resumen agregado del gusto en Cine y TV (base del resource MCP y la web)."""

    movies_watched: int
    shows_watched: int
    episodes_watched: int
    hours: float
    top_movies: list[TopMovie]
    top_shows: list[TopShow]
    recently_watched: list[RecentWatch]
    last_synced_at: datetime | None = None


def _media_type(item: NormalizedItem) -> str:
    value = item.work.extra.get("media_type")
    return value if isinstance(value, str) else ""


def _watched_at(item: NormalizedItem) -> datetime | None:
    value = item.work.extra.get("last_watched_at")
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_film_summary(
    items: list[NormalizedItem],
    stats: TraktStats | None,
    *,
    synced_at: datetime | None = None,
    top_limit: int = 10,
) -> FilmSummary:
    """Agrega películas y series en el resumen, con totales de `/stats`."""
    movies = [i for i in items if _media_type(i) == "movie"]
    shows = [i for i in items if _media_type(i) == "show"]

    top_movies = [
        TopMovie(
            title=i.work.title,
            year=i.work.year,
            plays=i.engagement.get("plays", 0),
        )
        for i in sorted(
            movies, key=lambda i: i.engagement.get("plays", 0), reverse=True
        )[:top_limit]
    ]
    top_shows = [
        TopShow(
            title=i.work.title,
            episodes_watched=i.engagement.get("episodes_watched", 0),
        )
        for i in sorted(
            shows, key=lambda i: i.engagement.get("episodes_watched", 0), reverse=True
        )[:top_limit]
    ]

    with_date = [(i, w) for i in items if (w := _watched_at(i)) is not None]
    with_date.sort(key=lambda pair: pair[1], reverse=True)
    recently_watched = [
        RecentWatch(title=i.work.title, media_type=_media_type(i), watched_at=w)
        for i, w in with_date[:top_limit]
    ]

    minutes = (stats.movies_minutes + stats.episodes_minutes) if stats else 0
    return FilmSummary(
        movies_watched=stats.movies_watched if stats else len(movies),
        shows_watched=stats.shows_watched if stats else len(shows),
        episodes_watched=stats.episodes_watched if stats else 0,
        hours=round(minutes / 60, 1),
        top_movies=top_movies,
        top_shows=top_shows,
        recently_watched=recently_watched,
        last_synced_at=synced_at,
    )
