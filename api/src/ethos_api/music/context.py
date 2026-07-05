"""Contexto descargable de música: `music.context.json` (D24/D39)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.music.summary import MusicSummary


def build_music_context(summary: MusicSummary) -> dict[str, object]:
    """Arma el contexto de música (misma información que sirve el MCP)."""
    return {
        "namespace": "music.*",
        "provider": "listenbrainz",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "scrobbles_total": summary.scrobbles_total,
            "scrobbles_window": summary.scrobbles_window,
            "window_days": summary.window_days,
            "last_listened_at": (
                summary.last_listened_at.isoformat()
                if summary.last_listened_at
                else None
            ),
        },
        "top_artists": [entry.model_dump() for entry in summary.top_artists],
        "top_tracks": [entry.model_dump() for entry in summary.top_tracks],
    }
