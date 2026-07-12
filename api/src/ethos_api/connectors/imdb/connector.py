"""Conector de IMDb: parsea el CSV de ratings y lo normaliza (D62).

IMDb no tiene API pública de usuario: el usuario exporta sus puntuaciones
(Your Ratings → Export, solo en la web de escritorio) y sube el CSV. Cada
fila es una obra puntuada: película o serie según `Title Type`, nota 1-10 y
fecha de puntuación como aproximación de visionado.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Columnas mínimas que identifican el export de ratings de IMDb.
REQUIRED_COLUMNS = frozenset({"Const", "Your Rating", "Title"})


class ImdbImportError(ValueError):
    """El archivo subido no es un export de ratings de IMDb válido."""


@dataclass
class ImdbRawData:
    """Contenido crudo del CSV de ratings de IMDb."""

    csv_text: str


def _is_show(title_type: str) -> bool:
    return "series" in title_type.lower()


class ImdbConnector(Connector[ImdbRawData, NormalizedItem]):
    """Conector del proveedor IMDb (categoría Cine y TV, import)."""

    id: ClassVar[str] = "imdb"
    category: ClassVar[Category] = Category.film
    ingest_mode: ClassVar[IngestMode] = IngestMode.import_
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "rating", "external_ids", "tags"}
    )

    def normalize(self, raw: ImdbRawData) -> list[NormalizedItem]:
        reader = csv.DictReader(io.StringIO(raw.csv_text))
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ImdbImportError(
                "El archivo no parece el export de ratings de IMDb: faltan "
                "columnas " + ", ".join(sorted(missing))
            )
        items: list[NormalizedItem] = []
        seen: set[str] = set()
        for row in reader:
            item = self._normalize_row(row)
            if item is None:
                continue
            const = item.work.external_ids.get("imdb", "")
            if const in seen:
                continue
            seen.add(const)
            items.append(item)
        return items

    def _normalize_row(self, row: dict[str, Any]) -> NormalizedItem | None:
        title = str(row.get("Title") or "").strip()
        const = str(row.get("Const") or "").strip()
        if not title or not const:
            return None
        title_type = str(row.get("Title Type") or "").strip()
        media_type = "show" if _is_show(title_type) else "movie"
        rating = self._parse_int(str(row.get("Your Rating") or ""))
        rated_at = self._parse_date(str(row.get("Date Rated") or "").strip())
        genres = [
            genre.strip()
            for genre in str(row.get("Genres") or "").split(",")
            if genre.strip()
        ]
        extra: dict[str, object] = {"media_type": media_type}
        if title_type:
            extra["title_type"] = title_type
        if rated_at is not None:
            extra["last_watched_at"] = rated_at.isoformat()
        return NormalizedItem(
            work=Work(
                title=title,
                year=self._parse_int(str(row.get("Year") or "")),
                external_ids={"imdb": const},
                extra=extra,
            ),
            category=Category.film,
            status=ItemStatus.consumed,
            # IMDb puntúa 1-10 → 0-100.
            rating_normalized=rating * 10 if rating else None,
            rating_original=str(rating) if rating else None,
            finished_at=rated_at,
            engagement={"plays": 1},
            tags=genres,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "rating": self.id},
        )

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
