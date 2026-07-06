"""Persistencia del slice de Libros: puerto, memoria y Supabase (D47).

Mismo modelo item que las demás categorías de obra (D35/D42): reutiliza
`user_items` y `source_state` con `category=books`, sin migración nueva. La
fuente es un import (Goodreads), así que `mode=import` en el estado.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ethos_api.items.support import keep_manual, manual_external_id
from ethos_api.schema import Category, NormalizedItem
from ethos_api.sources_status import (
    DB_TO_STATE,
    STATE_TO_DB,
    SourceStatus,
    SyncState,
)
from ethos_api.supabase_rest import SupabaseRest


class BooksStore(Protocol):
    """Persistencia de los libros normalizados por usuario."""

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None: ...

    def items_for_user(self, user_id: str) -> list[NormalizedItem]: ...

    def add_item(self, user_id: str, item: NormalizedItem) -> None: ...

    def delete_item(self, user_id: str, external_id: str) -> bool: ...

    def set_status(self, user_id: str, status: SourceStatus) -> None: ...

    def status_for_user(self, user_id: str) -> SourceStatus: ...


class InMemoryBooksStore:
    """Implementación en memoria (no persistente), para tests y desarrollo."""

    def __init__(self) -> None:
        self._items: dict[str, list[NormalizedItem]] = {}
        self._status: dict[str, SourceStatus] = {}

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        # Conserva las entradas a mano; el refresco solo reemplaza lo del proveedor.
        self._items[user_id] = keep_manual(self._items.get(user_id, [])) + list(items)

    def items_for_user(self, user_id: str) -> list[NormalizedItem]:
        return list(self._items.get(user_id, []))

    def add_item(self, user_id: str, item: NormalizedItem) -> None:
        self._items.setdefault(user_id, []).append(item)

    def delete_item(self, user_id: str, external_id: str) -> bool:
        items = self._items.get(user_id, [])
        kept = [i for i in items if manual_external_id(i) != external_id]
        self._items[user_id] = kept
        return len(kept) != len(items)

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._status[user_id] = status

    def status_for_user(self, user_id: str) -> SourceStatus:
        return self._status.get(user_id, SourceStatus())


class SupabaseBooksStore:
    """Respaldo en `user_items` + `source_state` vía PostgREST (D47)."""

    _ITEMS = "user_items"
    _STATE = "source_state"
    _CATEGORY = Category.books.value

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def _category_params(self, user_id: str) -> dict[str, str]:
        return {"user_id": f"eq.{user_id}", "category": f"eq.{self._CATEGORY}"}

    def _row(self, user_id: str, item: NormalizedItem) -> dict[str, object]:
        external_id = (
            manual_external_id(item)
            if item.source == "manual"
            else item.work.external_ids.get("goodreads", "")
        )
        return {
            "user_id": user_id,
            "category": self._CATEGORY,
            "external_id": external_id,
            "status": item.status.value,
            "title": item.work.title,
            # Columna indexada genérica: aquí guarda las páginas, la métrica.
            "playtime_minutes": item.engagement.get("pages", 0),
            "payload": item.model_dump(mode="json"),
        }

    def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
        # No borra las entradas a mano (external_id `manual:*`): el refresco
        # del proveedor solo reemplaza lo suyo.
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
                    "provider": "goodreads",
                    "mode": "import",
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
