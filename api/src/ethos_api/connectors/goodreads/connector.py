"""Conector de Goodreads: parsea el export CSV y lo normaliza al contrato (D47).

Goodreads no tiene API pública: el usuario descarga su biblioteca
(My Books → Import and export → Export Library) y sube el CSV. El conector
valida las columnas mínimas, mapea el shelf exclusivo al vocabulario común y
extrae rating, páginas, autor y fechas.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Columnas mínimas que identifican un export de Goodreads.
REQUIRED_COLUMNS = frozenset({"Title", "Author", "Exclusive Shelf"})

# Shelf exclusivo de Goodreads → vocabulario común (D47).
_SHELF_MAP = {
    "read": ItemStatus.consumed,
    "currently-reading": ItemStatus.in_progress,
    "to-read": ItemStatus.wishlist,
}


class GoodreadsImportError(ValueError):
    """El archivo subido no es un export de Goodreads válido."""


@dataclass
class GoodreadsRawData:
    """Contenido crudo del export CSV de Goodreads."""

    csv_text: str


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y/%m/%d").replace(tzinfo=UTC)
    except ValueError:
        return None


def _parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def _clean_isbn(value: str) -> str:
    # Goodreads exporta los ISBN como fórmula ("=""9780306406157""").
    return value.replace("=", "").replace('"', "").strip()


class GoodreadsConnector(Connector[GoodreadsRawData, NormalizedItem]):
    """Conector del proveedor Goodreads (categoría Libros, import)."""

    id: ClassVar[str] = "goodreads"
    category: ClassVar[Category] = Category.books
    ingest_mode: ClassVar[IngestMode] = IngestMode.import_
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "creators", "status", "rating", "review", "engagement", "external_ids"}
    )

    def normalize(self, raw: GoodreadsRawData) -> list[NormalizedItem]:
        reader = csv.DictReader(io.StringIO(raw.csv_text))
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise GoodreadsImportError(
                "El archivo no parece un export de Goodreads: faltan columnas "
                + ", ".join(sorted(missing))
            )
        items = []
        for row in reader:
            item = self._normalize_row(row)
            if item is not None:
                items.append(item)
        return items

    def _normalize_row(self, row: dict[str, Any]) -> NormalizedItem | None:
        title = (row.get("Title") or "").strip()
        if not title:
            return None
        author = (row.get("Author") or "").strip()
        shelf = (row.get("Exclusive Shelf") or "").strip()
        status = _SHELF_MAP.get(shelf, ItemStatus.in_library)

        rating = _parse_int((row.get("My Rating") or "0").strip())
        pages = _parse_int((row.get("Number of Pages") or "0").strip())
        read_count = _parse_int((row.get("Read Count") or "0").strip())
        year = _parse_int(
            (row.get("Original Publication Year") or row.get("Year Published") or "0").strip()
        )

        external_ids: dict[str, str] = {}
        book_id = (row.get("Book Id") or "").strip()
        if book_id:
            external_ids["goodreads"] = book_id
        isbn13 = _clean_isbn(row.get("ISBN13") or "")
        if isbn13:
            external_ids["isbn13"] = isbn13

        review = (row.get("My Review") or "").strip()
        return NormalizedItem(
            work=Work(
                title=title,
                creators=[author] if author else [],
                year=year or None,
                external_ids=external_ids,
                extra={"shelf": shelf} if shelf else {},
            ),
            category=Category.books,
            status=status,
            rating_normalized=rating * 20 if rating > 0 else None,
            rating_original=str(rating) if rating > 0 else None,
            added_at=_parse_date((row.get("Date Added") or "").strip()),
            finished_at=_parse_date((row.get("Date Read") or "").strip()),
            engagement={"pages": pages, "read_count": read_count},
            review=review or None,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "rating": self.id},
        )
