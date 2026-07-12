"""Conector de Spotify: parsea el export de historial y lo normaliza (D62).

Spotify cerró su API de historial: el usuario pide sus datos en
privacy.spotify.com ("Historial de streaming ampliado", hasta 30 días) y sube
cada `Streaming_History_Audio_*.json`. Se soportan los dos formatos del
export: el ampliado (`ts`, `ms_played`, `master_metadata_*`) y el de datos de
cuenta (`endTime`, `artistName`, `trackName`, `msPlayed`). Las reproducciones
de menos de 30 segundos se descartan (el criterio de "escucha" de Spotify).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, NormalizedEvent

# Umbral de escucha real: menos de 30 s no cuenta como reproducción.
MIN_PLAYED_MS = 30_000


class SpotifyImportError(ValueError):
    """El archivo subido no es un historial de Spotify válido."""


@dataclass
class SpotifyRawData:
    """Contenido crudo de un archivo JSON del export de Spotify."""

    json_text: str


def looks_like_spotify(records: list[Any]) -> bool:
    """True si la lista parece un historial de Spotify (cualquier formato)."""
    if not records or not isinstance(records[0], dict):
        return False
    first = records[0]
    extended = "ts" in first and "ms_played" in first
    simple = "endTime" in first and "msPlayed" in first
    return extended or simple


class SpotifyConnector(Connector[SpotifyRawData, NormalizedEvent]):
    """Conector del proveedor Spotify (categoría Música, import)."""

    id: ClassVar[str] = "spotify"
    category: ClassVar[Category] = Category.music
    ingest_mode: ClassVar[IngestMode] = IngestMode.import_
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"artist", "track", "release", "occurred_at"}
    )

    def normalize(self, raw: SpotifyRawData) -> list[NormalizedEvent]:
        try:
            records = json.loads(raw.json_text)
        except json.JSONDecodeError as error:
            raise SpotifyImportError(
                "El archivo no es un JSON válido del export de Spotify"
            ) from error
        if not isinstance(records, list) or not looks_like_spotify(records):
            raise SpotifyImportError(
                "El archivo no parece un historial de Spotify: sube los "
                "Streaming_History_Audio_*.json (o StreamingHistory*.json) "
                "de tu export"
            )
        events: list[NormalizedEvent] = []
        for record in records:
            event = self._normalize_record(record)
            if event is not None:
                events.append(event)
        return events

    def _normalize_record(self, record: dict[str, Any]) -> NormalizedEvent | None:
        if "ts" in record:
            # Formato ampliado.
            played_ms = int(record.get("ms_played") or 0)
            track = str(record.get("master_metadata_track_name") or "").strip()
            artist = str(record.get("master_metadata_album_artist_name") or "").strip()
            release = str(record.get("master_metadata_album_album_name") or "").strip()
            occurred_raw = str(record.get("ts") or "")
        else:
            # Formato simple del export de datos de cuenta.
            played_ms = int(record.get("msPlayed") or 0)
            track = str(record.get("trackName") or "").strip()
            artist = str(record.get("artistName") or "").strip()
            release = ""
            occurred_raw = str(record.get("endTime") or "")
        if played_ms < MIN_PLAYED_MS or not track or not artist:
            return None
        occurred_at = self._parse_when(occurred_raw)
        if occurred_at is None:
            return None
        payload = {"artist": artist, "track": track}
        if release:
            payload["release"] = release
        return NormalizedEvent(
            category=Category.music,
            occurred_at=occurred_at,
            payload=payload,
            source=self.id,
        )

    @staticmethod
    def _parse_when(value: str) -> datetime | None:
        # Ampliado: ISO 8601 con Z ("2024-03-01T18:22:05Z").
        # Simple: "2024-03-01 18:22" (hora local, se asume UTC).
        for parser in (
            lambda v: datetime.fromisoformat(v.replace("Z", "+00:00")),
            lambda v: datetime.strptime(v, "%Y-%m-%d %H:%M").replace(tzinfo=UTC),
        ):
            try:
                parsed = parser(value)
            except ValueError:
                continue
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        return None
