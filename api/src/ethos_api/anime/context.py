"""Contexto descargable de Anime y manga: `anime.context.json` (D24/D46)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.anime.summary import AnimeSummary


def build_anime_context(summary: AnimeSummary) -> dict[str, object]:
    """Arma el contexto de Anime y manga (misma información que sirve el MCP)."""
    return {
        "namespace": "anime.*",
        "provider": "anilist",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "anime_watched": summary.anime_watched,
            "manga_read": summary.manga_read,
            "episodes_watched": summary.episodes_watched,
            "chapters_read": summary.chapters_read,
            "mean_score": summary.mean_score,
            "last_synced_at": (
                summary.last_synced_at.isoformat() if summary.last_synced_at else None
            ),
        },
        "top_rated": [t.model_dump(mode="json") for t in summary.top_rated],
        "current": [c.model_dump(mode="json") for c in summary.current],
    }
