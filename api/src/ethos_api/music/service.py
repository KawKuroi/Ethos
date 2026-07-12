"""Refresco e import de la fuente de música (D40/D62).

API (ListenBrainz D37, Last.fm D62): refresco incremental — trae solo los
listens posteriores al último `occurred_at` guardado. Al conectar (o cambiar
de proveedor, D4) el primer refresco reemplaza el conjunto (`replace=True`).

Import (Spotify, Apple Music): síncrono; cada archivo se combina con los
eventos existentes del mismo proveedor (los exports llegan en varios
archivos), deduplicado y con tope claro para cuidar el almacén.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.connectors.lastfm.client import LastfmApiError
from ethos_api.connectors.lastfm.connector import LastfmConnector, LastfmRawData
from ethos_api.connectors.listenbrainz.connector import (
    ListenBrainzConnector,
    ListenBrainzRawData,
)
from ethos_api.music.store import EventStore
from ethos_api.schema import NormalizedEvent
from ethos_api.sources_status import SourceStatus, SyncState

# Tope de eventos que conserva un import (los exports de Spotify traen años
# de historial): se quedan los más recientes.
MAX_IMPORTED_EVENTS = 10_000

# Códigos de Last.fm que indican usuario no accesible (inexistente o privado).
_NOT_ACCESSIBLE = frozenset({403, 404})


class ListenBrainzApi(Protocol):
    """Superficie del cliente de ListenBrainz que usa el refresco (testeable)."""

    def get_listens(
        self, user_name: str, *, min_ts: int | None = ..., count: int = ...
    ) -> dict[str, Any]: ...


class LastfmApi(Protocol):
    """Superficie del cliente de Last.fm que usa el refresco (testeable)."""

    def get_recent_tracks(
        self, user_name: str, *, from_ts: int | None = ..., page: int = ..., limit: int = ...
    ) -> dict[str, Any]: ...


def refresh_user_music(
    user_id: str,
    user_name: str,
    client: ListenBrainzApi,
    store: EventStore,
    *,
    replace: bool = False,
) -> None:
    """Sincroniza los listens nuevos de ListenBrainz (incremental, D40)."""
    _set_status(store, user_id, "listenbrainz", "api", SyncState.syncing)
    connector = ListenBrainzConnector()
    try:
        latest = None if replace else store.latest_occurred_at(user_id)
        min_ts = int(latest.timestamp()) if latest else None
        raw = ListenBrainzRawData(listens=client.get_listens(user_name, min_ts=min_ts))
        events = connector.normalize(raw)
        if replace:
            store.replace_events(user_id, events)
        else:
            store.append_events(user_id, events)
        _set_status(
            store,
            user_id,
            "listenbrainz",
            "api",
            SyncState.fresh,
            synced_at=datetime.now(UTC),
        )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        _set_status(
            store, user_id, "listenbrainz", "api", SyncState.error, detail=str(error)
        )


def refresh_user_music_lastfm(
    user_id: str,
    user_name: str,
    client: LastfmApi,
    store: EventStore,
    *,
    replace: bool = False,
) -> None:
    """Sincroniza los scrobbles nuevos de Last.fm (incremental, D62)."""
    _set_status(store, user_id, "lastfm", "api", SyncState.syncing)
    connector = LastfmConnector()
    try:
        latest = None if replace else store.latest_occurred_at(user_id)
        from_ts = int(latest.timestamp()) if latest else None
        raw = LastfmRawData(
            pages=[client.get_recent_tracks(user_name, from_ts=from_ts)]
        )
        events = connector.normalize(raw)
        if replace:
            store.replace_events(user_id, events)
        else:
            store.append_events(user_id, events)
        _set_status(
            store,
            user_id,
            "lastfm",
            "api",
            SyncState.fresh,
            synced_at=datetime.now(UTC),
        )
    except LastfmApiError as error:
        if error.status_code in _NOT_ACCESSIBLE:
            store.replace_events(user_id, [])
            _set_status(
                store,
                user_id,
                "lastfm",
                "api",
                SyncState.private,
                detail=(
                    "Tu usuario de Last.fm no existe o su historial es privado; "
                    "revísalo y vuelve a conectar"
                ),
            )
        else:
            _set_status(
                store, user_id, "lastfm", "api", SyncState.error, detail=str(error)
            )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        _set_status(
            store, user_id, "lastfm", "api", SyncState.error, detail=str(error)
        )


def import_music_events(
    user_id: str,
    provider: str,
    events: list[NormalizedEvent],
    store: EventStore,
) -> int:
    """Importa eventos de un export y devuelve cuántos quedaron guardados.

    Si el proveedor coincide con la fuente actual, combina (los exports llegan
    en varios archivos); si es otro proveedor, reemplaza (D4). Deduplicado por
    (timestamp, artista, pista) y con tope `MAX_IMPORTED_EVENTS`.
    """
    current = store.status_for_user(user_id)
    base = store.events_for_user(user_id) if current.provider == provider else []
    merged: dict[tuple[str, str, str], NormalizedEvent] = {}
    for event in base + events:
        key = (
            event.occurred_at.isoformat(),
            event.payload.get("artist", ""),
            event.payload.get("track", ""),
        )
        merged[key] = event
    kept = sorted(merged.values(), key=lambda e: e.occurred_at, reverse=True)
    kept = kept[:MAX_IMPORTED_EVENTS]
    store.replace_events(user_id, kept)
    _set_status(
        store,
        user_id,
        provider,
        "import",
        SyncState.fresh,
        synced_at=datetime.now(UTC),
    )
    return len(kept)


def _set_status(
    store: EventStore,
    user_id: str,
    provider: str,
    mode: str,
    state: SyncState,
    *,
    synced_at: datetime | None = None,
    detail: str | None = None,
) -> None:
    store.set_status(
        user_id,
        SourceStatus(
            state=state,
            synced_at=synced_at,
            detail=detail,
            provider=provider,
            mode=mode,
        ),
    )
