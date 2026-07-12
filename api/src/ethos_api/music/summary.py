"""Resumen de música desde los eventos (listens), con ventana temporal (D39)."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel

from ethos_api.schema import NormalizedEvent

DEFAULT_WINDOW_DAYS = 30

# Duración media aproximada de una canción; ninguna fuente de escuchas
# almacenada trae duración, así que el tiempo de escucha se estima.
_AVG_TRACK_MINUTES = 3.5


class TopEntry(BaseModel):
    """Entrada de un ranking (artista, track o álbum) con su número de escuchas."""

    name: str
    count: int


class PeakWeekday(BaseModel):
    """Día de la semana con más escuchas en la ventana (0 = lunes)."""

    weekday: int
    count: int


class MusicSummary(BaseModel):
    """Resumen del gusto musical: totales, ritmo y rankings de una ventana.

    Los derivados (artistas distintos, descubrimientos, día pico, álbum top)
    salen de los propios eventos; `top_release` queda en None si la fuente no
    trae álbum (p. ej. Apple Music).
    """

    scrobbles_total: int
    scrobbles_window: int
    window_days: int
    top_artists: list[TopEntry]
    top_tracks: list[TopEntry]
    # Variedad y ritmo de la ventana.
    distinct_artists_window: int = 0
    avg_per_day_window: float = 0.0
    # Artistas cuya primera escucha registrada cae dentro de la ventana.
    new_artists_window: int = 0
    # Tiempo de escucha estimado (escuchas x ~3,5 min); la web lo marca con ≈.
    estimated_hours_window: float = 0.0
    peak_weekday: PeakWeekday | None = None
    top_release: TopEntry | None = None
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
    release_counts: Counter[str] = Counter()
    weekday_counts: Counter[int] = Counter()
    for event in in_window:
        artist = event.payload.get("artist", "")
        track = event.payload.get("track", "")
        release = event.payload.get("release", "")
        if artist:
            artist_counts[artist] += 1
        if track and artist:
            track_counts[f"{track} — {artist}"] += 1
        if release and artist:
            release_counts[f"{release} — {artist}"] += 1
        weekday_counts[event.occurred_at.weekday()] += 1

    # Descubrimientos: artistas que no suenan en ningún evento anterior a la
    # ventana (su primera escucha registrada cae dentro).
    seen_before = {
        artist
        for e in events
        if e.occurred_at < cutoff and (artist := e.payload.get("artist", ""))
    }
    new_artists = sum(1 for a in artist_counts if a not in seen_before)

    peak = weekday_counts.most_common(1)
    top_release = _top(release_counts, 1)

    last = max((e.occurred_at for e in events), default=None)
    return MusicSummary(
        scrobbles_total=len(events),
        scrobbles_window=len(in_window),
        window_days=window_days,
        top_artists=_top(artist_counts, top_limit),
        top_tracks=_top(track_counts, top_limit),
        distinct_artists_window=len(artist_counts),
        avg_per_day_window=round(len(in_window) / window_days, 1) if window_days else 0.0,
        new_artists_window=new_artists,
        estimated_hours_window=round(len(in_window) * _AVG_TRACK_MINUTES / 60, 1),
        peak_weekday=(
            PeakWeekday(weekday=peak[0][0], count=peak[0][1]) if peak else None
        ),
        top_release=top_release[0] if top_release else None,
        last_listened_at=last,
    )
