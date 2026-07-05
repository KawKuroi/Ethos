"""Persistencia del slice de Cine y TV: puerto, memoria y Supabase (D42).

Mismo modelo item que Juegos (D35): reutiliza `user_items` y `source_state`
con `category=film`, sin migración nueva. Los agregados de Trakt (`TraktStats`)
se guardan en `provider_profile`, como el perfil de Steam.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from ethos_api.connectors.trakt.connector import TraktStats
from ethos_api.schema import Category, NormalizedItem
from ethos_api.sources_status import (
    DB_TO_STATE,
    STATE_TO_DB,
    SourceStatus,
    SyncState,
)
from ethos_api.supabase_rest import SupabaseRest


class FilmStore(Protocol):
    """Persistencia de las películas y series normalizadas por usuario."""

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None: ...

    def items_for_user(self, user_id: str) -> list[NormalizedItem]: ...

    def set_stats(self, user_id: str, stats: TraktStats) -> None: ...

    def stats_for_user(self, user_id: str) -> TraktStats | None: ...

    def set_status(self, user_id: str, status: SourceStatus) -> None: ...

    def status_for_user(self, user_id: str) -> SourceStatus: ...


class InMemoryFilmStore:
    """Implementación en memoria (no persistente), para tests y desarrollo."""

    def __init__(self) -> None:
        self._items: dict[str, list[NormalizedItem]] = {}
        self._stats: dict[str, TraktStats] = {}
        self._status: dict[str, SourceStatus] = {}

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        self._items[user_id] = list(items)

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        return list(self._items.get(user_id, []))

    def set_stats(self, user_id: str, stats: TraktStats) -> None:
        self._stats[user_id] = stats

    def stats_for_user(self, user_id: str) -> TraktStats | None:
        return self._stats.get(user_id)

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._status[user_id] = status

    def status_for_user(self, user_id: str) -> SourceStatus:
        return self._status.get(user_id, SourceStatus())


class SupabaseFilmStore:
    """Respaldo en `user_items` + `source_state` vía PostgREST (D42)."""

    _ITEMS = "user_items"
    _STATE = "source_state"
    _CATEGORY = Category.film.value

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def _category_params(self, user_id: str) -> dict[str, str]:
        return {"user_id": f"eq.{user_id}", "category": f"eq.{self._CATEGORY}"}

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        self._rest.delete(self._ITEMS, self._category_params(user_id))
        self._rest.insert(
            self._ITEMS,
            [
                {
                    "user_id": user_id,
                    "category": self._CATEGORY,
                    "external_id": item.work.external_ids.get("trakt", ""),
                    "status": item.status.value,
                    "title": item.work.title,
                    "playtime_minutes": item.engagement.get("plays", 0),
                    "payload": item.model_dump(mode="json"),
                }
                for item in items
            ],
        )

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        rows = self._rest.select(
            self._ITEMS,
            {**self._category_params(user_id), "select": "payload"},
        )
        return [NormalizedItem.model_validate(row["payload"]) for row in rows]

    def set_stats(self, user_id: str, stats: TraktStats) -> None:
        self._upsert_state(
            user_id,
            {
                "provider_profile": {
                    "movies_watched": stats.movies_watched,
                    "movies_minutes": stats.movies_minutes,
                    "shows_watched": stats.shows_watched,
                    "episodes_watched": stats.episodes_watched,
                    "episodes_minutes": stats.episodes_minutes,
                }
            },
        )

    def stats_for_user(self, user_id: str) -> TraktStats | None:
        rows = self._rest.select(
            self._STATE,
            {**self._category_params(user_id), "select": "provider_profile", "limit": "1"},
        )
        if not rows or not rows[0].get("provider_profile"):
            return None
        data = rows[0]["provider_profile"]
        return TraktStats(
            movies_watched=int(data.get("movies_watched", 0)),
            movies_minutes=int(data.get("movies_minutes", 0)),
            shows_watched=int(data.get("shows_watched", 0)),
            episodes_watched=int(data.get("episodes_watched", 0)),
            episodes_minutes=int(data.get("episodes_minutes", 0)),
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
        self._rest.upsert(
            self._STATE,
            [
                {
                    "user_id": user_id,
                    "category": self._CATEGORY,
                    "provider": "trakt",
                    "mode": "api",
                    **fields,
                }
            ],
            on_conflict="user_id,category",
        )
