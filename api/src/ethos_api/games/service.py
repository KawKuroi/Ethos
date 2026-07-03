"""Refresco de la fuente de juegos: fetch → normalizar → persistir (D36).

Corre en segundo plano (BackgroundTasks). El cálculo de completado tiene
presupuesto fijo (D33): una llamada por juego solo para el top por horas,
protegida por el throttle del cliente de Steam.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.connectors.steam.connector import SteamConnector, SteamRawData
from ethos_api.games.store import GamesStore, SourceStatus, SyncState

# Juegos (top por horas) para los que se calcula el completado por refresco.
COMPLETION_BUDGET = 20
_PUBLIC_VISIBILITY = 3


class SteamGamesApi(Protocol):
    """Superficie del cliente de Steam que usa el refresco (testeable)."""

    def get_owned_games(self, steamid: str) -> dict[str, Any]: ...

    def get_recently_played(self, steamid: str) -> dict[str, Any]: ...

    def get_player_summary(self, steamid: str) -> dict[str, Any]: ...

    def get_wishlist(self, steamid: str) -> dict[str, Any]: ...

    def get_player_achievements(self, steamid: str, appid: int) -> dict[str, Any]: ...


def refresh_user_games(
    user_id: str,
    steamid: str,
    client: SteamGamesApi,
    store: GamesStore,
) -> None:
    """Sincroniza la biblioteca de un usuario y deja el estado de frescura."""
    store.set_status(user_id, SourceStatus(state=SyncState.syncing))
    connector = SteamConnector()
    try:
        raw = SteamRawData(
            owned_games=client.get_owned_games(steamid),
            player_summary=client.get_player_summary(steamid),
        )
        profile = connector.profile(raw)
        store.set_profile(user_id, profile)

        if profile.visibility != _PUBLIC_VISIBILITY:
            # Perfil privado: Steam devuelve la biblioteca vacía. Se deja el
            # estado explícito para que la web guíe a hacerlo público.
            store.replace_items(user_id, [])
            store.set_status(
                user_id,
                SourceStatus(
                    state=SyncState.private,
                    detail="El perfil de Steam es privado; no se pueden leer sus datos",
                ),
            )
            return

        raw.recently_played = _safe(client.get_recently_played, steamid)
        raw.wishlist = _safe(client.get_wishlist, steamid)
        raw.completion_by_appid = _completion_for_top(
            client, connector, steamid, raw.owned_games
        )

        store.replace_items(user_id, connector.normalize(raw))
        store.set_status(
            user_id,
            SourceStatus(state=SyncState.fresh, synced_at=datetime.now(UTC)),
        )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        store.set_status(
            user_id, SourceStatus(state=SyncState.error, detail=str(error))
        )


def _safe(call: Any, steamid: str) -> dict[str, Any]:
    """Llamada tolerante: un extra que falla no tumba el refresco completo."""
    try:
        result: dict[str, Any] = call(steamid)
    except Exception:  # degradar a vacío es intencional
        return {}
    return result


def _completion_for_top(
    client: SteamGamesApi,
    connector: SteamConnector,
    steamid: str,
    owned_games: dict[str, Any],
) -> dict[int, float]:
    """Completado (0-100) para el top por horas, dentro del presupuesto D33."""
    games = owned_games.get("response", {}).get("games", [])
    top = sorted(
        games, key=lambda g: int(g.get("playtime_forever", 0)), reverse=True
    )[:COMPLETION_BUDGET]

    completion: dict[int, float] = {}
    for game in top:
        appid = int(game["appid"])
        try:
            payload = client.get_player_achievements(steamid, appid)
        except Exception:  # noqa: S112 — juego sin logros o error puntual.
            continue
        pct = connector.completion_from_achievements(payload)
        if pct is not None:
            completion[appid] = pct
    return completion
