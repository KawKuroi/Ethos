"""Contexto descargable de juegos: `games.context.json` (D24/D34)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.connectors.steam.connector import SteamProfile
from ethos_api.games.summary import GamesSummary
from ethos_api.schema import ItemStatus, NormalizedItem

# Cuántos appids de la wishlist viajan en el contexto, por prioridad.
_WISHLIST_TOP = 20


def build_games_context(
    summary: GamesSummary,
    items: list[NormalizedItem],
    profile: SteamProfile | None,
) -> dict[str, object]:
    """Arma el contexto de juegos con la forma fijada en D34.

    Es la misma información en origen que sirve el MCP: resumen agregado,
    top por horas, actividad reciente y wishlist. Sin histórico de eventos
    en v1.
    """
    wishlist = [i for i in items if i.status is ItemStatus.wishlist]
    by_priority = sorted(
        wishlist,
        key=lambda i: (
            int(p) if isinstance(p := i.work.extra.get("wishlist_priority"), int) else 1_000_000
        ),
    )
    top_priority_appids = [
        appid
        for i in by_priority[:_WISHLIST_TOP]
        if (appid := i.work.external_ids.get("steam_appid"))
    ]

    profile_block: dict[str, object] | None = None
    if profile:
        profile_block = {
            "persona_name": profile.persona_name,
            "steamid": profile.steamid,
            "visibility": profile.visibility,
        }

    return {
        "namespace": "games.*",
        "provider": "steam",
        "generated_at": datetime.now(UTC).isoformat(),
        "profile": profile_block,
        "summary": {
            "games": summary.games,
            "hours": summary.hours,
            "wishlisted": summary.wishlisted,
            "avg_completion_pct": summary.avg_completion_pct,
            "last_synced_at": (
                summary.last_synced_at.isoformat() if summary.last_synced_at else None
            ),
        },
        "top_by_hours": [t.model_dump() for t in summary.top_by_hours],
        "recently_played": [r.model_dump() for r in summary.recently_played],
        # Géneros dominantes del top por horas, enriquecidos de la store (D55).
        "top_genres": [g.model_dump() for g in summary.top_genres],
        # Los títulos de la wishlist se difieren (D32): Steam no los devuelve
        # en la wishlist y resolverlos exige una llamada de store por juego.
        "wishlist": {
            "count": summary.wishlisted,
            "top_priority_appids": top_priority_appids,
        },
    }
