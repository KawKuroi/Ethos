"""Persistencia de eventos de música: puerto, memoria y Supabase (D38).

Reutiliza `SourceStatus`/`SyncState` (frescura genérica) y la tabla
`source_state`; los eventos viven en `user_events` (migración 0004), indexados
por usuario/categoría/`occurred_at` para las consultas por ventana.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ethos_api.schema import Category, NormalizedEvent
from ethos_api.sources_status import (
    DB_TO_STATE,
    STATE_TO_DB,
    SourceStatus,
    SyncState,
)
from ethos_api.supabase_rest import SupabaseRest


class EventStore(Protocol):
    """Persistencia de eventos normalizados por usuario y categoría."""

    def append_events(self, user_id: str, events: list[NormalizedEvent]) -> None: ...

    def replace_events(self, user_id: str, events: list[NormalizedEvent]) -> None: ...

    def events_for_user(self, user_id: str) -> list[NormalizedEvent]: ...

    def latest_occurred_at(self, user_id: str) -> datetime | None: ...

    def set_status(self, user_id: str, status: SourceStatus) -> None: ...

    def status_for_user(self, user_id: str) -> SourceStatus: ...


class InMemoryEventStore:
    """Implementación en memoria (no persistente), para tests y desarrollo."""

    def __init__(self) -> None:
        self._events: dict[str, list[NormalizedEvent]] = {}
        self._status: dict[str, SourceStatus] = {}

    def append_events(self, user_id: str, events: list[NormalizedEvent]) -> None:
        bucket = self._events.setdefault(user_id, [])
        bucket.extend(events)
        # Del más reciente al más antiguo, como los espera el resumen.
        bucket.sort(key=lambda e: e.occurred_at, reverse=True)

    def replace_events(self, user_id: str, events: list[NormalizedEvent]) -> None:
        # Un import reemplaza el conjunto (una fuente activa por categoría, D4).
        self._events[user_id] = []
        self.append_events(user_id, events)

    def events_for_user(self, user_id: str) -> list[NormalizedEvent]:
        return list(self._events.get(user_id, []))

    def latest_occurred_at(self, user_id: str) -> datetime | None:
        events = self._events.get(user_id)
        return events[0].occurred_at if events else None

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._status[user_id] = status

    def status_for_user(self, user_id: str) -> SourceStatus:
        return self._status.get(user_id, SourceStatus())


class SupabaseEventStore:
    """Respaldo en `user_events` + `source_state` vía PostgREST (D38)."""

    _EVENTS = "user_events"
    _STATE = "source_state"
    _CATEGORY = Category.music.value

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def _category_params(self, user_id: str) -> dict[str, str]:
        return {"user_id": f"eq.{user_id}", "category": f"eq.{self._CATEGORY}"}

    # Tamaño de lote de inserción: un import grande (Spotify) no debe viajar
    # en un solo POST a PostgREST.
    _INSERT_CHUNK = 1000

    def append_events(self, user_id: str, events: list[NormalizedEvent]) -> None:
        rows = [
            {
                "user_id": user_id,
                "category": self._CATEGORY,
                "occurred_at": event.occurred_at.isoformat(),
                "payload": event.payload,
            }
            for event in events
        ]
        for start in range(0, len(rows), self._INSERT_CHUNK):
            self._rest.insert(self._EVENTS, rows[start : start + self._INSERT_CHUNK])

    def replace_events(self, user_id: str, events: list[NormalizedEvent]) -> None:
        # Un import reemplaza el conjunto (una fuente activa por categoría, D4).
        self._rest.delete(self._EVENTS, self._category_params(user_id))
        self.append_events(user_id, events)

    def events_for_user(self, user_id: str) -> list[NormalizedEvent]:
        rows = self._rest.select(
            self._EVENTS,
            {
                **self._category_params(user_id),
                "select": "occurred_at,payload",
                "order": "occurred_at.desc",
            },
        )
        # El origen real vive en source_state.provider (multi-proveedor).
        source = self.status_for_user(user_id).provider or "listenbrainz"
        return [
            NormalizedEvent(
                category=Category.music,
                occurred_at=datetime.fromisoformat(row["occurred_at"]),
                payload=row["payload"],
                source=source,
            )
            for row in rows
        ]

    def latest_occurred_at(self, user_id: str) -> datetime | None:
        rows = self._rest.select(
            self._EVENTS,
            {
                **self._category_params(user_id),
                "select": "occurred_at",
                "order": "occurred_at.desc",
                "limit": "1",
            },
        )
        return datetime.fromisoformat(rows[0]["occurred_at"]) if rows else None

    def set_status(self, user_id: str, status: SourceStatus) -> None:
        self._rest.upsert(
            self._STATE,
            [
                {
                    "user_id": user_id,
                    "category": self._CATEGORY,
                    "provider": status.provider or "listenbrainz",
                    "mode": status.mode or "api",
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
                "select": "status,detail,last_synced_at,provider,mode",
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
            provider=row.get("provider"),
            mode=row.get("mode"),
        )
