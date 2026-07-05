"""Generador del resumen de Anime y manga desde los registros normalizados (D46)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ethos_api.schema import ItemStatus, NormalizedItem


class TopRatedEntry(BaseModel):
    """Entrada del top por nota del usuario (0-100)."""

    title: str
    media_type: str
    score: int
    progress: int


class CurrentEntry(BaseModel):
    """Obra en curso (viéndose o leyéndose), con su progreso."""

    title: str
    media_type: str
    progress: int


class AnimeSummary(BaseModel):
    """Resumen agregado de Anime y manga (base del resource MCP y la web)."""

    anime_watched: int
    manga_read: int
    episodes_watched: int
    chapters_read: int
    mean_score: float | None
    top_rated: list[TopRatedEntry]
    current: list[CurrentEntry]
    last_synced_at: datetime | None = None


def _media_type(item: NormalizedItem) -> str:
    value = item.work.extra.get("media_type")
    return value if isinstance(value, str) else ""


def _progress(item: NormalizedItem) -> int:
    return item.engagement.get("episodes_progress", 0) or item.engagement.get(
        "chapters_read", 0
    )


def _updated_at(item: NormalizedItem) -> int:
    value = item.work.extra.get("updated_at")
    return value if isinstance(value, int) else 0


def build_anime_summary(
    items: list[NormalizedItem],
    *,
    synced_at: datetime | None = None,
    top_limit: int = 10,
) -> AnimeSummary:
    """Agrega animes y mangas en el resumen (conteos, nota media, tops, en curso)."""
    anime = [i for i in items if _media_type(i) == "anime"]
    manga = [i for i in items if _media_type(i) == "manga"]

    scores = [i.rating_normalized for i in items if i.rating_normalized is not None]
    mean_score = round(sum(scores) / len(scores), 1) if scores else None

    rated = [i for i in items if i.rating_normalized is not None]
    rated.sort(key=lambda i: i.rating_normalized or 0, reverse=True)
    top_rated = [
        TopRatedEntry(
            title=i.work.title,
            media_type=_media_type(i),
            score=i.rating_normalized or 0,
            progress=_progress(i),
        )
        for i in rated[:top_limit]
    ]

    in_progress = [i for i in items if i.status is ItemStatus.in_progress]
    in_progress.sort(key=_updated_at, reverse=True)
    current = [
        CurrentEntry(title=i.work.title, media_type=_media_type(i), progress=_progress(i))
        for i in in_progress[:top_limit]
    ]

    return AnimeSummary(
        anime_watched=sum(1 for i in anime if i.status is ItemStatus.consumed),
        manga_read=sum(1 for i in manga if i.status is ItemStatus.consumed),
        episodes_watched=sum(_progress(i) for i in anime),
        chapters_read=sum(_progress(i) for i in manga),
        mean_score=mean_score,
        top_rated=top_rated,
        current=current,
        last_synced_at=synced_at,
    )
