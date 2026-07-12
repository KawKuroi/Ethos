"""Conector de Apple Music: parsea el export de historial y lo normaliza (D62).

Apple no tiene API de historial: el usuario pide sus datos en
privacy.apple.com (Apple Media Services, hasta 7 días) y sube el CSV
`Apple Music - Play History Daily Tracks.csv`. El archivo agrega por día y
pista ("Artist - Track" en `Track Description`), así que cada fila se
normaliza como un evento con las reproducciones del día en el payload
(limitación de origen: no hay hora exacta por escucha).
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, NormalizedEvent

# Columnas mínimas que identifican el Play History Daily Tracks.
REQUIRED_COLUMNS = frozenset({"Track Description", "Date Played"})


class AppleMusicImportError(ValueError):
    """El archivo subido no es un export de Apple Music válido."""


@dataclass
class AppleMusicRawData:
    """Contenido crudo del CSV `Play History Daily Tracks`."""

    csv_text: str


class AppleMusicConnector(Connector[AppleMusicRawData, NormalizedEvent]):
    """Conector del proveedor Apple Music (categoría Música, import)."""

    id: ClassVar[str] = "applemusic"
    category: ClassVar[Category] = Category.music
    ingest_mode: ClassVar[IngestMode] = IngestMode.import_
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"artist", "track", "occurred_at"}
    )

    def normalize(self, raw: AppleMusicRawData) -> list[NormalizedEvent]:
        reader = csv.DictReader(io.StringIO(raw.csv_text))
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise AppleMusicImportError(
                "El archivo no parece el Play History Daily Tracks de Apple "
                "Music: faltan columnas " + ", ".join(sorted(missing))
            )
        events: list[NormalizedEvent] = []
        for row in reader:
            event = self._normalize_row(row)
            if event is not None:
                events.append(event)
        return events

    def _normalize_row(self, row: dict[str, Any]) -> NormalizedEvent | None:
        description = str(row.get("Track Description") or "").strip()
        occurred_at = self._parse_date(str(row.get("Date Played") or "").strip())
        if not description or occurred_at is None:
            return None
        # "Artist - Track"; una fila sin ambos lados no aporta a los tops.
        artist, separator, track = description.partition(" - ")
        artist = artist.strip()
        track = track.strip()
        if not separator or not artist or not track:
            return None
        payload = {"artist": artist, "track": track}
        plays = str(row.get("Play Count") or "").strip()
        if plays.isdigit() and int(plays) > 0:
            payload["plays"] = plays
        return NormalizedEvent(
            category=Category.music,
            occurred_at=occurred_at,
            payload=payload,
            source=self.id,
        )

    @staticmethod
    def _parse_date(value: str) -> datetime | None:
        # `Date Played` viene como "20240301" (AAAAMMDD).
        try:
            return datetime.strptime(value, "%Y%m%d").replace(tzinfo=UTC)
        except ValueError:
            return None
