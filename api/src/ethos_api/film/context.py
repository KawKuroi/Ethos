"""Contexto descargable de Cine y TV: `film.context.json` (D24/D43)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.context_history import items_history
from ethos_api.film.summary import FilmSummary
from ethos_api.schema import NormalizedItem


def build_film_context(
    summary: FilmSummary, items: list[NormalizedItem]
) -> dict[str, object]:
    """Arma el contexto de Cine y TV (misma información que sirve el MCP)."""
    return {
        "namespace": "film.*",
        "provider": "trakt",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "movies_watched": summary.movies_watched,
            "shows_watched": summary.shows_watched,
            "episodes_watched": summary.episodes_watched,
            "hours": summary.hours,
            "last_synced_at": (
                summary.last_synced_at.isoformat() if summary.last_synced_at else None
            ),
        },
        "top_movies": [m.model_dump(mode="json") for m in summary.top_movies],
        "top_shows": [s.model_dump(mode="json") for s in summary.top_shows],
        "recently_watched": [
            r.model_dump(mode="json") for r in summary.recently_watched
        ],
        # Detalle completo de lo visto hasta el límite, con metadatos (D60).
        "history": items_history(items),
    }
