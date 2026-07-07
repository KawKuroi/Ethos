"""Generador del resumen de juegos desde los registros normalizados."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ethos_api.connectors.steam.connector import SteamProfile
from ethos_api.schema import ItemStatus, NormalizedItem


class TopGame(BaseModel):
    """Entrada del top por horas."""

    title: str
    hours: float
    completion_pct: float | None = None
    # Géneros de la ficha de store, enriquecidos con presupuesto (D55).
    genres: list[str] = []


class RecentGame(BaseModel):
    """Juego con actividad en las últimas dos semanas."""

    title: str
    hours_2weeks: float


class TopGenre(BaseModel):
    """Género agregado del top por horas (D55)."""

    name: str
    games: int


class GamesSummary(BaseModel):
    """Resumen agregado del gusto en juegos (base del resource MCP y la web)."""

    games: int
    hours: float
    wishlisted: int
    avg_completion_pct: float | None
    top_by_hours: list[TopGame]
    recently_played: list[RecentGame]
    # Géneros dominantes entre los juegos enriquecidos (el top por horas).
    top_genres: list[TopGenre] = []
    persona_name: str | None = None
    last_synced_at: datetime | None = None


def _hours(minutes: int) -> float:
    return round(minutes / 60, 1)


def build_games_summary(
    items: list[NormalizedItem],
    profile: SteamProfile | None,
    *,
    synced_at: datetime | None = None,
    top_limit: int = 10,
) -> GamesSummary:
    """Agrega la biblioteca normalizada en el resumen de juegos."""
    library = [i for i in items if i.status is ItemStatus.in_library]
    wishlist = [i for i in items if i.status is ItemStatus.wishlist]

    total_minutes = sum(i.engagement.get("playtime_minutes", 0) for i in library)

    completions = [
        pct
        for i in library
        if isinstance(pct := i.work.extra.get("completion_pct"), int | float)
    ]
    avg_completion = round(sum(completions) / len(completions), 1) if completions else None

    by_hours = sorted(
        library, key=lambda i: i.engagement.get("playtime_minutes", 0), reverse=True
    )
    top = [
        TopGame(
            title=i.work.title,
            hours=_hours(i.engagement.get("playtime_minutes", 0)),
            completion_pct=(
                float(pct)
                if isinstance(pct := i.work.extra.get("completion_pct"), int | float)
                else None
            ),
            genres=_genres_of(i),
        )
        for i in by_hours[:top_limit]
        if i.engagement.get("playtime_minutes", 0) > 0
    ]

    # Géneros dominantes entre los juegos enriquecidos (solo el top por horas
    # trae géneros, D55): conteo de juegos por género, orden descendente.
    genre_counts: dict[str, int] = {}
    for item in library:
        for genre in _genres_of(item):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    top_genres = [
        TopGenre(name=name, games=count)
        for name, count in sorted(genre_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    ]

    recent = sorted(
        (i for i in library if i.engagement.get("playtime_2weeks_minutes", 0) > 0),
        key=lambda i: i.engagement.get("playtime_2weeks_minutes", 0),
        reverse=True,
    )
    recently_played = [
        RecentGame(
            title=i.work.title,
            hours_2weeks=_hours(i.engagement.get("playtime_2weeks_minutes", 0)),
        )
        for i in recent
    ]

    return GamesSummary(
        games=len(library),
        hours=_hours(total_minutes),
        wishlisted=len(wishlist),
        avg_completion_pct=avg_completion,
        top_by_hours=top,
        recently_played=recently_played,
        top_genres=top_genres,
        persona_name=profile.persona_name if profile else None,
        last_synced_at=synced_at,
    )


def _genres_of(item: NormalizedItem) -> list[str]:
    genres = item.work.extra.get("genres")
    if not isinstance(genres, list):
        return []
    return [str(g) for g in genres]
