"""Conector de Trakt: normaliza películas y series vistas al contrato común."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work


@dataclass
class TraktRawData:
    """Respuestas crudas de Trakt para un usuario."""

    watched_movies: list[dict[str, Any]] = field(default_factory=list)
    watched_shows: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraktStats:
    """Agregados de `/users/{u}/stats` (conteos y minutos totales)."""

    movies_watched: int
    movies_minutes: int
    shows_watched: int
    episodes_watched: int
    episodes_minutes: int


class TraktConnector(Connector[TraktRawData, NormalizedItem]):
    """Conector del proveedor Trakt (categoría Cine y TV)."""

    id: ClassVar[str] = "trakt"
    category: ClassVar[Category] = Category.film
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "engagement", "external_ids"}
    )

    def normalize(self, raw: TraktRawData) -> list[NormalizedItem]:
        items = [self._normalize_movie(entry) for entry in raw.watched_movies]
        items.extend(self._normalize_show(entry) for entry in raw.watched_shows)
        return items

    def _normalize_movie(self, entry: dict[str, Any]) -> NormalizedItem:
        movie = entry.get("movie", {})
        engagement = {"plays": int(entry.get("plays", 0))}
        extra: dict[str, object] = {"media_type": "movie"}
        last_watched = entry.get("last_watched_at")
        if last_watched:
            extra["last_watched_at"] = str(last_watched)
        return NormalizedItem(
            work=self._work(movie, extra),
            category=Category.film,
            status=ItemStatus.consumed,
            engagement=engagement,
            source=self.id,
            provenance={"title": self.id, "engagement": self.id},
        )

    def _normalize_show(self, entry: dict[str, Any]) -> NormalizedItem:
        show = entry.get("show", {})
        episodes = sum(
            len(season.get("episodes", [])) for season in entry.get("seasons", [])
        )
        engagement = {
            "plays": int(entry.get("plays", 0)),
            "episodes_watched": episodes,
        }
        extra: dict[str, object] = {"media_type": "show"}
        last_watched = entry.get("last_watched_at")
        if last_watched:
            extra["last_watched_at"] = str(last_watched)
        return NormalizedItem(
            work=self._work(show, extra),
            category=Category.film,
            status=ItemStatus.consumed,
            engagement=engagement,
            source=self.id,
            provenance={"title": self.id, "engagement": self.id},
        )

    @staticmethod
    def _work(media: dict[str, Any], extra: dict[str, object]) -> Work:
        ids = media.get("ids", {})
        external_ids = {
            key: str(ids[key])
            for key in ("trakt", "slug", "imdb", "tmdb")
            if ids.get(key) is not None
        }
        year = media.get("year")
        return Work(
            title=str(media.get("title", "")),
            year=int(year) if year is not None else None,
            external_ids=external_ids,
            extra=extra,
        )

    @staticmethod
    def stats(raw: TraktRawData) -> TraktStats:
        """Extrae los agregados totales desde la respuesta de `/stats`."""
        movies = raw.stats.get("movies", {})
        shows = raw.stats.get("shows", {})
        episodes = raw.stats.get("episodes", {})
        return TraktStats(
            movies_watched=int(movies.get("watched", 0)),
            movies_minutes=int(movies.get("minutes", 0)),
            shows_watched=int(shows.get("watched", 0)),
            episodes_watched=int(episodes.get("watched", 0)),
            episodes_minutes=int(episodes.get("minutes", 0)),
        )
