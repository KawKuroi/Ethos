"""Generador del resumen de Cine y TV desde los registros normalizados (D43)."""

from __future__ import annotations

from collections import Counter
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


class TopRatedFilm(BaseModel):
    """Obra del top por nota del usuario (0-100)."""

    title: str
    year: int | None = None
    media_type: str
    rating: int


class RatingBucket(BaseModel):
    """Franja de la distribución de notas, en estrellas (1-5)."""

    stars: int
    count: int


class TopFilmGenre(BaseModel):
    """Género agregado de las obras con géneros (import de IMDb)."""

    name: str
    works: int


class FilmSummary(BaseModel):
    """Resumen agregado del gusto en Cine y TV (base del resource MCP y la web).

    Los campos de notas, géneros y década solo se rellenan si la fuente los
    trae (Letterboxd/IMDb puntúan; Trakt no): la web oculta lo que falte.
    """

    movies_watched: int
    shows_watched: int
    episodes_watched: int
    hours: float
    top_movies: list[TopMovie]
    top_shows: list[TopShow]
    recently_watched: list[RecentWatch]
    # Notas del usuario (Letterboxd, IMDb o entradas a mano).
    mean_rating: float | None = None
    rated_count: int = 0
    rating_buckets: list[RatingBucket] = []
    top_rated: list[TopRatedFilm] = []
    # Obras vistas más de una vez: la señal de favoritas más honesta.
    rewatched_count: int = 0
    # Géneros dominantes (IMDb los importa como tags).
    top_genres: list[TopFilmGenre] = []
    # Década con más obras vistas (por año de estreno).
    favorite_decade: int | None = None
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

    rated = [i for i in items if i.rating_normalized is not None]
    mean_rating = (
        round(sum(i.rating_normalized or 0 for i in rated) / len(rated), 1)
        if rated
        else None
    )
    top_rated = [
        TopRatedFilm(
            title=i.work.title,
            year=i.work.year,
            media_type=_media_type(i),
            rating=i.rating_normalized or 0,
        )
        for i in sorted(rated, key=lambda i: i.rating_normalized or 0, reverse=True)[
            :top_limit
        ]
    ]
    star_counts = Counter(_stars(i.rating_normalized or 0) for i in rated)
    rating_buckets = (
        [RatingBucket(stars=s, count=star_counts.get(s, 0)) for s in range(1, 6)]
        if rated
        else []
    )

    rewatched_count = sum(1 for i in movies if i.engagement.get("plays", 0) > 1)

    genre_counts = Counter(tag for i in items for tag in i.tags)
    top_genres = [
        TopFilmGenre(name=name, works=count)
        for name, count in sorted(genre_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    ]

    decade_counts = Counter(
        (i.work.year // 10) * 10 for i in items if i.work.year is not None
    )
    favorite_decade = (
        # A igual conteo gana la década más reciente (criterio estable).
        max(decade_counts, key=lambda d: (decade_counts[d], d))
        if decade_counts
        else None
    )

    minutes = (stats.movies_minutes + stats.episodes_minutes) if stats else 0
    return FilmSummary(
        movies_watched=stats.movies_watched if stats else len(movies),
        shows_watched=stats.shows_watched if stats else len(shows),
        episodes_watched=stats.episodes_watched if stats else 0,
        hours=round(minutes / 60, 1),
        top_movies=top_movies,
        top_shows=top_shows,
        recently_watched=recently_watched,
        mean_rating=mean_rating,
        rated_count=len(rated),
        rating_buckets=rating_buckets,
        top_rated=top_rated,
        rewatched_count=rewatched_count,
        top_genres=top_genres,
        favorite_decade=favorite_decade,
        last_synced_at=synced_at,
    )


def _stars(rating: int) -> int:
    """Nota 0-100 → franja de estrellas 1-5 (0-20 → 1★ … 81-100 → 5★)."""
    return min(5, max(1, -(-rating // 20)))
