"""Conector de ListenBrainz: normaliza listens a eventos con timestamp."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, NormalizedEvent


@dataclass
class ListenBrainzRawData:
    """Respuesta cruda de `GET /1/user/{user}/listens`."""

    listens: dict[str, Any]


class ListenBrainzConnector(Connector[ListenBrainzRawData, NormalizedEvent]):
    """Conector del proveedor ListenBrainz (categoría Música)."""

    id: ClassVar[str] = "listenbrainz"
    category: ClassVar[Category] = Category.music
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"artist", "track", "release", "occurred_at"}
    )

    def normalize(self, raw: ListenBrainzRawData) -> list[NormalizedEvent]:
        listens = raw.listens.get("payload", {}).get("listens", [])
        events: list[NormalizedEvent] = []
        for listen in listens:
            event = self._normalize_listen(listen)
            if event is not None:
                events.append(event)
        return events

    def _normalize_listen(self, listen: dict[str, Any]) -> NormalizedEvent | None:
        listened_at = listen.get("listened_at")
        metadata = listen.get("track_metadata", {})
        track = str(metadata.get("track_name", "")).strip()
        artist = str(metadata.get("artist_name", "")).strip()
        if listened_at is None or not track or not artist:
            # Un listen sin timestamp o sin obra no aporta a las consultas.
            return None
        payload = {"artist": artist, "track": track}
        release = str(metadata.get("release_name", "")).strip()
        if release:
            payload["release"] = release
        return NormalizedEvent(
            category=Category.music,
            occurred_at=datetime.fromtimestamp(int(listened_at), tz=UTC),
            payload=payload,
            source=self.id,
        )

    @staticmethod
    def latest_listened_at(raw: ListenBrainzRawData) -> int | None:
        """Mayor `listened_at` de la respuesta (llave del refresco incremental)."""
        listens = raw.listens.get("payload", {}).get("listens", [])
        stamps = [int(listen["listened_at"]) for listen in listens if listen.get("listened_at")]
        return max(stamps) if stamps else None
