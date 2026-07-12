"""Conector de StoryGraph: parsea el export CSV y lo normaliza (D62).

StoryGraph no tiene API pública: el usuario exporta su biblioteca (Manage
Account → Manage Your Data → Export StoryGraph Library) y sube el CSV. Misma
forma que Goodreads (D47): shelf → status, nota 0-5 con medios → 0-100,
autor en `creators` y fechas de lectura.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Columnas mínimas que identifican el export de StoryGraph.
REQUIRED_COLUMNS = frozenset({"Title", "Authors", "Read Status"})

# Read Status de StoryGraph → vocabulario común.
_STATUS_MAP = {
    "read": ItemStatus.consumed,
    "currently-reading": ItemStatus.in_progress,
    "to-read": ItemStatus.wishlist,
    "did-not-finish": ItemStatus.abandoned,
}


class StorygraphImportError(ValueError):
    """El archivo subido no es un export de StoryGraph válido."""


@dataclass
class StorygraphRawData:
    """Contenido crudo del export CSV de StoryGraph."""

    csv_text: str


class StorygraphConnector(Connector[StorygraphRawData, NormalizedItem]):
    """Conector del proveedor StoryGraph (categoría Libros, import)."""

    id: ClassVar[str] = "storygraph"
    category: ClassVar[Category] = Category.books
    ingest_mode: ClassVar[IngestMode] = IngestMode.import_
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "creators", "status", "rating", "review", "tags", "external_ids"}
    )

    def normalize(self, raw: StorygraphRawData) -> list[NormalizedItem]:
        reader = csv.DictReader(io.StringIO(raw.csv_text))
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise StorygraphImportError(
                "El archivo no parece un export de StoryGraph: faltan columnas "
                + ", ".join(sorted(missing))
            )
        items = []
        seen: set[str] = set()
        for row in reader:
            item = self._normalize_row(row)
            if item is None:
                continue
            key = item.work.external_ids.get("storygraph", "")
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
        return items

    def _normalize_row(self, row: dict[str, Any]) -> NormalizedItem | None:
        title = str(row.get("Title") or "").strip()
        if not title:
            return None
        authors = [
            author.strip()
            for author in str(row.get("Authors") or "").split(",")
            if author.strip()
        ]
        read_status = str(row.get("Read Status") or "").strip().lower()
        status = _STATUS_MAP.get(read_status, ItemStatus.in_library)
        # Star Rating 0-5 con medios (4.5) → 0-100; vacío = sin puntuar.
        rating_raw = str(row.get("Star Rating") or "").strip()
        rating = self._parse_rating(rating_raw)
        isbn = str(row.get("ISBN/UID") or "").strip()
        read_count = self._parse_int(str(row.get("Read Count") or ""))
        tags = [
            tag.strip()
            for tag in str(row.get("Tags") or "").split(",")
            if tag.strip()
        ]
        review = str(row.get("Review") or "").strip()
        # `user_items` exige external_id único: sin ISBN/UID se deriva uno
        # estable del título y el autor.
        fallback = "-".join((title + " " + (authors[0] if authors else "")).lower().split())
        external_ids: dict[str, str] = {"storygraph": isbn or fallback}
        if isbn and len(isbn) == 13 and isbn.isdigit():
            external_ids["isbn13"] = isbn
        return NormalizedItem(
            work=Work(
                title=title,
                creators=authors,
                external_ids=external_ids,
                extra={"shelf": read_status} if read_status else {},
            ),
            category=Category.books,
            status=status,
            rating_normalized=rating,
            rating_original=rating_raw or None,
            added_at=self._parse_date(str(row.get("Date Added") or "").strip()),
            finished_at=self._parse_date(str(row.get("Last Date Read") or "").strip()),
            engagement={
                "pages": 0,
                "read_count": read_count or (1 if status is ItemStatus.consumed else 0),
            },
            review=review or None,
            tags=tags,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "rating": self.id},
        )

    @staticmethod
    def _parse_rating(value: str) -> int | None:
        try:
            rating = float(value)
        except ValueError:
            return None
        return round(rating * 20) if rating > 0 else None

    @staticmethod
    def _parse_int(value: str) -> int:
        try:
            return int(float(value))
        except ValueError:
            return 0

    @staticmethod
    def _parse_date(value: str) -> datetime | None:
        for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None
