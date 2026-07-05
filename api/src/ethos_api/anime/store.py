"""Persistencia del slice de Anime y manga: puerto, memoria y Supabase (D46).

Mismo modelo item que Juegos y Cine y TV (D35/D42): reutiliza `user_items` y
`source_state` con `category=anime`, sin migración nueva. AniList no tiene
agregados de perfil aparte: el resumen se calcula desde los items.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ethos_api.schema import Category, NormalizedItem
from ethos_api.sources_status import (
    DB_TO_STATE,
    STATE_TO_DB,
    SourceStatus,
    SyncState,
)
from ethos_api.supabase_rest import SupabaseRest


class AnimeStore(Protocol):
    """Persistencia de los animes y mangas normalizados por usuario."""

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None: ...

    def items_for_user(self, user_id: str) -> list[NormalizedItem]: ...

    def set_status(self, user_id: str, status: SourceStatus) -> None: ...

    def status_for_user(self, user_id: str) -> SourceStatus: ...


class InMemoryAnimeStore:
    """Implementación en memoria (no persistente), para tests y desarrollo."""

    def __init__(self) -> None:
        self._items: dict[str, list[NormalizedItem]] = {}
        self._status: dict[str, SourceStatus] = {}

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        self._items[user_id] = list(items)

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        return list(self._items.get(user_id, []))

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._status[user_id] = status

    def status_for_user(self, user_id: str) -> SourceStatus:
        return self._status.get(user_id, SourceStatus())


class SupabaseAnimeStore:
    """Respaldo en `user_items` + `source_state` vía PostgREST (D46)."""

    _ITEMS = "user_items"
    _STATE = "source_state"
    _CATEGORY = Category.anime.value

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
                    "external_id": item.work.external_ids.get("anilist", ""),
                    "status": item.status.value,
                    "title": item.work.title,
                    # Columna indexada genérica: aquí guarda el progreso
                    # (episodios o capítulos), la métrica de la categoría.
                    "playtime_minutes": item.engagement.get("episodes_progress", 0)
                    or item.engagement.get("chapters_read", 0),
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

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._rest.upsert(
            self._STATE,
            [
                {
                    "user_id": user_id,
                    "category": self._CATEGORY,
                    "provider": "anilist",
                    "mode": "api",
                    "status": STATE_TO_DB[status.state],
                    "detail": status.detail,
                    "last_synced_at": (
                        status.synced_at.isoformat() if status.synced_at else None
                    ),
                }
            ],
            on_conflict="user_id,category",
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
        synced_at = (
            datetime.fromisoformat(row["last_synced_at"])
            if row.get("last_synced_at")
            else None
        )
        return SourceStatus(
            state=DB_TO_STATE.get(row.get("status", ""), SyncState.never),
            synced_at=synced_at,
            detail=row.get("detail"),
        )
