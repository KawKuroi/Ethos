"""Resumen de música desde los eventos (listens), con ventana temporal (D39)."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel

from ethos_api.schema import NormalizedEvent

DEFAULT_WINDOW_DAYS = 30


class TopEntry(BaseModel):
    """Entrada de un ranking (artista o track) con su número de escuchas."""

    name: str
    count: int


class MusicSummary(BaseModel):
    """Resumen del gusto musical: totales y rankings de una ventana."""

    scrobbles_total: int
    scrobbles_window: int
    window_days: int
    top_artists: list[TopEntry]
    top_tracks: list[TopEntry]
    last_listened_at: datetime | None = None


def _top(counter: Counter[str], limit: int) -> list[TopEntry]:
    return [TopEntry(name=name, count=count) for name, count in counter.most_common(limit)]


def build_music_summary(
    events: list[NormalizedEvent],
    *,
    window_days: int = DEFAULT_WINDOW_DAYS,
    now: datetime | None = None,
    top_limit: int = 10,
) -> MusicSummary:
    """Agrega los listens en totales + top artistas/tracks de la ventana."""
    now = now or datetime.now(UTC)
    cutoff = now - timedelta(days=window_days)
    in_window = [e for e in events if e.occurred_at >= cutoff]

    artist_counts: Counter[str] = Counter()
    track_counts: Counter[str] = Counter()
    for event in in_window:
        artist = event.payload.get("artist", "")
        track = event.payload.get("track", "")
        if artist:
            artist_counts[artist] += 1
        if track and artist:
            track_counts[f"{track} — {artist}"] += 1

    last = max((e.occurred_at for e in events), default=None)
    return MusicSummary(
        scrobbles_total=len(events),
        scrobbles_window=len(in_window),
        window_days=window_days,
        top_artists=_top(artist_counts, top_limit),
        top_tracks=_top(track_counts, top_limit),
        last_listened_at=last,
    )
