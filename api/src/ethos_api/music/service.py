"""Refresco incremental de la fuente de música (D40).

Trae solo los listens posteriores al último `occurred_at` guardado (llave de
cambio = timestamp del último listen) y los añade al store.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.connectors.listenbrainz.connector import (
    ListenBrainzConnector,
    ListenBrainzRawData,
)
from ethos_api.music.store import EventStore
from ethos_api.sources_status import SourceStatus, SyncState


class ListenBrainzApi(Protocol):
    """Superficie del cliente de ListenBrainz que usa el refresco (testeable)."""

    def get_listens(
        self, user_name: str, *, min_ts: int | None = ..., count: int = ...
    ) -> dict[str, Any]: ...


def refresh_user_music(
    user_id: str,
    user_name: str,
    client: ListenBrainzApi,
    store: EventStore,
) -> None:
    """Sincroniza los listens nuevos de un usuario y deja el estado de frescura."""
    store.set_status(user_id, SourceStatus(state=SyncState.syncing))
    connector = ListenBrainzConnector()
    try:
        latest = store.latest_occurred_at(user_id)
        min_ts = int(latest.timestamp()) if latest else None
        raw = ListenBrainzRawData(listens=client.get_listens(user_name, min_ts=min_ts))
        store.append_events(user_id, connector.normalize(raw))
        store.set_status(
            user_id, SourceStatus(state=SyncState.fresh, synced_at=datetime.now(UTC))
        )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        store.set_status(
            user_id, SourceStatus(state=SyncState.error, detail=str(error))
        )
