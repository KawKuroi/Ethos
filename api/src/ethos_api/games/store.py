"""Persistencia del slice de juegos: puerto, memoria y respaldo Supabase (D35).

Mismo patrón que las credenciales (D20): un `Protocol` como puerto, memoria
indexada para desarrollo/tests y el respaldo real en las tablas `user_items`
y `source_state` (migración 0003, RLS owner-only).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from ethos_api.connectors.steam.connector import SteamProfile
from ethos_api.items.support import keep_manual, manual_external_id
from ethos_api.schema import Category, NormalizedItem
from ethos_api.sources_status import (
    DB_TO_STATE,
    STATE_TO_DB,
    SourceStatus,
    SyncState,
)
from ethos_api.supabase_rest import SupabaseRest

# Reexport para compatibilidad: otros módulos importan estos desde games.store.
__all__ = [
    "DB_TO_STATE",
    "STATE_TO_DB",
    "GamesStore",
    "InMemoryGamesStore",
    "SourceStatus",
    "SupabaseGamesStore",
    "SyncState",
]


class GamesStore(Protocol):
    """Persistencia de los juegos normalizados por usuario."""

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None: ...

    def items_for_user(self, user_id: str) -> list[NormalizedItem]: ...

    def add_item(self, user_id: str, item: NormalizedItem) -> None: ...

    def delete_item(self, user_id: str, external_id: str) -> bool: ...

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
        # Conserva las entradas a mano; el refresco solo reemplaza lo del proveedor.
        merged = keep_manual(self._items.get(user_id, [])) + list(items)
        self._items[user_id] = merged
        # Índice por appid para consultas puntuales sin recorrer la lista.
        self._by_appid[user_id] = {
            appid: item
            for item in merged
            if (appid := item.work.external_ids.get("steam_appid"))
        }

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        return list(self._items.get(user_id, []))

    def add_item(self, user_id: str, item: NormalizedItem) -> None:
        self._items.setdefault(user_id, []).append(item)
        if appid := item.work.external_ids.get("steam_appid"):
            self._by_appid.setdefault(user_id, {})[appid] = item

    def delete_item(self, user_id: str, external_id: str) -> bool:
        items = self._items.get(user_id, [])
        kept = [i for i in items if manual_external_id(i) != external_id]
        self._items[user_id] = kept
        return len(kept) != len(items)

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


class SupabaseGamesStore:
    """Respaldo en `user_items` + `source_state` vía PostgREST (D35)."""

    _ITEMS = "user_items"
    _STATE = "source_state"
    _CATEGORY = Category.games.value

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def _category_params(self, user_id: str) -> dict[str, str]:
        return {"user_id": f"eq.{user_id}", "category": f"eq.{self._CATEGORY}"}

    def _row(self, user_id: str, item: NormalizedItem) -> dict[str, object]:
        external_id = (
            manual_external_id(item)
            if item.source == "manual"
            else item.work.external_ids.get("steam_appid", "")
        )
        return {
            "user_id": user_id,
            "category": self._CATEGORY,
            "external_id": external_id,
            "status": item.status.value,
            "title": item.work.title,
            "playtime_minutes": item.engagement.get("playtime_minutes", 0),
            "payload": item.model_dump(mode="json"),
        }

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        # No borra las entradas a mano (external_id `manual:*`).
        self._rest.delete(
            self._ITEMS,
            {**self._category_params(user_id), "external_id": "not.like.manual:*"},
        )
        self._rest.insert(self._ITEMS, [self._row(user_id, item) for item in items])

    def add_item(self, user_id: str, item: NormalizedItem) -> None:
        self._rest.insert(self._ITEMS, [self._row(user_id, item)])

    def delete_item(self, user_id: str, external_id: str) -> bool:
        return (
            self._rest.delete(
                self._ITEMS,
                {**self._category_params(user_id), "external_id": f"eq.{external_id}"},
            )
            > 0
        )

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        rows = self._rest.select(
            self._ITEMS,
            {
                **self._category_params(user_id),
                "select": "payload",
                "order": "playtime_minutes.desc",
            },
        )
        return [NormalizedItem.model_validate(row["payload"]) for row in rows]

    def set_profile(self, user_id: str, profile: SteamProfile) -> None:
        self._upsert_state(
            user_id,
            {
                "provider_profile": {
                    "steamid": profile.steamid,
                    "persona_name": profile.persona_name,
                    "avatar_url": profile.avatar_url,
                    "visibility": profile.visibility,
                }
            },
        )

    def profile_for_user(self, user_id: str) -> SteamProfile | None:
        rows = self._rest.select(
            self._STATE,
            {**self._category_params(user_id), "select": "provider_profile", "limit": "1"},
        )
        if not rows or not rows[0].get("provider_profile"):
            return None
        data = rows[0]["provider_profile"]
        return SteamProfile(
            steamid=data["steamid"],
            persona_name=data.get("persona_name", ""),
            avatar_url=data.get("avatar_url"),
            visibility=data.get("visibility"),
        )

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._upsert_state(
            user_id,
            {
                "status": STATE_TO_DB[status.state],
                "detail": status.detail,
                "last_synced_at": (
                    status.synced_at.isoformat() if status.synced_at else None
                ),
            },
        )

    def status_for_user(self, user_id: str) -> SourceStatus:
        rows = self._rest.select(
            self._STATE,
            {
                **self._category_params(user_id),
                "select": "status,detail,last_synced_at",
                "limit": "1",
            },
        )
        if not rows:
            return SourceStatus()
        row = rows[0]
        synced_at = None
        if row.get("last_synced_at"):
            synced_at = datetime.fromisoformat(row["last_synced_at"])
        return SourceStatus(
            state=DB_TO_STATE.get(row.get("status", ""), SyncState.never),
            synced_at=synced_at,
            detail=row.get("detail"),
        )

    def _upsert_state(self, user_id: str, fields: dict[str, Any]) -> None:
        # provider/mode completan el insert; el upsert conserva el resto.
        self._rest.upsert(
            self._STATE,
            [
                {
                    "user_id": user_id,
                    "category": self._CATEGORY,
                    "provider": "steam",
                    "mode": "api",
                    **fields,
                }
            ],
            on_conflict="user_id,category",
        )
