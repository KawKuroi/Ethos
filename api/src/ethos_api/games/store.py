"""Persistencia del slice de juegos: puerto e implementación en memoria (D35).

Mismo patrón que las credenciales (D20): un `Protocol` como puerto y una
implementación en memoria indexada, para que la migración a Supabase
(tabla `user_games` + RLS) sustituya solo esta pieza.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from ethos_api.connectors.steam.connector import SteamProfile
from ethos_api.schema import NormalizedItem


class SyncState(StrEnum):
    """Estado de frescura de la fuente de un usuario (D36)."""

    never = "never"
    syncing = "syncing"
    fresh = "fresh"
    private = "private"
    error = "error"


@dataclass
class SourceStatus:
    """Estado del refresco de la fuente de juegos de un usuario."""

    state: SyncState = SyncState.never
    synced_at: datetime | None = None
    detail: str | None = None


class GamesStore(Protocol):
    """Persistencia de los juegos normalizados por usuario."""

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None: ...

    def items_for_user(self, user_id: str) -> list[NormalizedItem]: ...

    def set_profile(self, user_id: str, profile: SteamProfile) -> None: ...

    def profile_for_user(self, user_id: str) -> SteamProfile | None: ...

    def set_status(self, user_id: str, status: SourceStatus) -> None: ...

    def status_for_user(self, user_id: str) -> SourceStatus: ...


class InMemoryGamesStore:
    """Implementación en memoria, indexada por usuario y appid.

    No persistente: al redeploy se pierde y se repuebla con un refresco. El
    respaldo Supabase llega con la infra (D35).
    """

    def __init__(self) -> None:
        self._items: dict[str, list[NormalizedItem]] = {}
        self._by_appid: dict[str, dict[str, NormalizedItem]] = {}
        self._profiles: dict[str, SteamProfile] = {}
        self._status: dict[str, SourceStatus] = {}

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        self._items[user_id] = list(items)
        # Índice por appid para consultas puntuales sin recorrer la lista.
        self._by_appid[user_id] = {
            appid: item
            for item in items
            if (appid := item.work.external_ids.get("steam_appid"))
        }

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        return list(self._items.get(user_id, []))

    def item_by_appid(self, user_id: str, appid: str) -> NormalizedItem | None:
        return self._by_appid.get(user_id, {}).get(appid)

    def set_profile(self, user_id: str, profile: SteamProfile) -> None:
        self._profiles[user_id] = profile

    def profile_for_user(self, user_id: str) -> SteamProfile | None:
        return self._profiles.get(user_id)

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._status[user_id] = status

    def status_for_user(self, user_id: str) -> SourceStatus:
        return self._status.get(user_id, SourceStatus())
