"""Conector de Letterboxd: parsea los CSV del export y los normaliza (D62).

El export de Letterboxd (Ajustes → Data → Export your data, gratis) es un ZIP
con varios CSV; se soportan los tres útiles subidos de uno en uno:
`diary.csv` (visionados con fecha, nota y rewatch), `watched.csv` (todo lo
visto) y `ratings.csv` (todo lo puntuado). Solo películas (Letterboxd no
registra series). Varias filas del diario para la misma película se agrupan
en un item con sus reproducciones.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Columnas comunes a los tres CSV del export.
BASE_COLUMNS = frozenset({"Date", "Name", "Year", "Letterboxd URI"})
# Columnas que identifican cada archivo (la detección prueba diary primero).
DIARY_COLUMNS = BASE_COLUMNS | {"Watched Date", "Rewatch"}
RATINGS_COLUMNS = BASE_COLUMNS | {"Rating"}
WATCHED_COLUMNS = BASE_COLUMNS


class LetterboxdImportError(ValueError):
    """El archivo subido no es un CSV del export de Letterboxd válido."""


@dataclass
class LetterboxdRawData:
    """Contenido crudo de un CSV del export (diary, watched o ratings)."""

    csv_text: str


class LetterboxdConnector(Connector[LetterboxdRawData, NormalizedItem]):
    """Conector del proveedor Letterboxd (categoría Cine y TV, import)."""

    id: ClassVar[str] = "letterboxd"
    category: ClassVar[Category] = Category.film
    ingest_mode: ClassVar[IngestMode] = IngestMode.import_
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "rating", "external_ids"}
    )

    def normalize(self, raw: LetterboxdRawData) -> list[NormalizedItem]:
        reader = csv.DictReader(io.StringIO(raw.csv_text))
        columns = set(reader.fieldnames or [])
        missing = BASE_COLUMNS - columns
        if missing:
            raise LetterboxdImportError(
                "El archivo no parece un CSV del export de Letterboxd: faltan "
                "columnas " + ", ".join(sorted(missing))
            )
        # Una película puede repetirse (rewatches en diary): se agrupa por URI.
        by_key: dict[str, NormalizedItem] = {}
        for row in reader:
            item = self._normalize_row(row)
            if item is None:
                continue
            key = item.work.external_ids.get("letterboxd", item.work.title)
            existing = by_key.get(key)
            by_key[key] = item if existing is None else self._merge(existing, item)
        return list(by_key.values())

    def _normalize_row(self, row: dict[str, Any]) -> NormalizedItem | None:
        title = str(row.get("Name") or "").strip()
        if not title:
            return None
        year = self._parse_int(str(row.get("Year") or ""))
        uri = str(row.get("Letterboxd URI") or "").strip()
        # El slug de la URI (https://boxd.it/xxxx o /film/slug/) como id;
        # sin URI se deriva uno estable del título (external_id único).
        slug = uri.rstrip("/").rsplit("/", 1)[-1] if uri else ""
        if not slug:
            slug = "-".join(f"{title} {year or ''}".lower().split())
        rating = self._parse_rating(str(row.get("Rating") or ""))
        watched_at = self._parse_date(
            str(row.get("Watched Date") or row.get("Date") or "").strip()
        )
        rewatch = str(row.get("Rewatch") or "").strip().lower() == "yes"
        extra: dict[str, object] = {"media_type": "movie"}
        if watched_at is not None:
            extra["last_watched_at"] = watched_at.isoformat()
        return NormalizedItem(
            work=Work(
                title=title,
                year=year,
                external_ids={"letterboxd": slug} if slug else {},
                extra=extra,
            ),
            category=Category.film,
            status=ItemStatus.consumed,
            rating_normalized=rating,
            rating_original=str(row.get("Rating")).strip() if rating else None,
            finished_at=watched_at,
            engagement={"plays": 2 if rewatch else 1},
            source=self.id,
            provenance={"title": self.id, "status": self.id},
        )

    @staticmethod
    def _merge(existing: NormalizedItem, new: NormalizedItem) -> NormalizedItem:
        """Combina dos filas de la misma película (rewatches del diario)."""
        latest = max(
            existing,
            new,
            key=lambda item: item.finished_at or datetime.min.replace(tzinfo=UTC),
        )
        merged = latest.model_copy(deep=True)
        merged.engagement["plays"] = (
            existing.engagement.get("plays", 1) + new.engagement.get("plays", 1)
        )
        merged.rating_normalized = (
            new.rating_normalized or existing.rating_normalized
        )
        merged.rating_original = new.rating_original or existing.rating_original
        return merged

    @staticmethod
    def _parse_rating(value: str) -> int | None:
        # Letterboxd puntúa 0,5-5 con medios; 0/vacío = sin puntuar → 0-100.
        try:
            rating = float(value)
        except ValueError:
            return None
        return round(rating * 20) if rating > 0 else None

    @staticmethod
    def _parse_int(value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_date(value: str) -> datetime | None:
        try:
            return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            return None
