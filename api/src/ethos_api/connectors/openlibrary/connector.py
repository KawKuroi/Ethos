"""Conector de Open Library: normaliza el reading log al contrato común (D62).

Misma forma que Goodreads (D47) para que el resumen de Libros funcione sin
cambios: autor en `creators`, páginas en `engagement` (Open Library no las da:
0) y fechas de la bitácora. El estante already-read usa `logged_date` como
aproximación de la fecha de término (la API no da fecha de lectura).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Estante del reading log → vocabulario común.
_SHELF_MAP = {
    "already-read": ItemStatus.consumed,
    "currently-reading": ItemStatus.in_progress,
    "want-to-read": ItemStatus.wishlist,
}


@dataclass
class OpenLibraryRawData:
    """Entradas crudas del reading log por estante."""

    shelves: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


class OpenLibraryConnector(Connector[OpenLibraryRawData, NormalizedItem]):
    """Conector del proveedor Open Library (categoría Libros, API)."""

    id: ClassVar[str] = "openlibrary"
    category: ClassVar[Category] = Category.books
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "creators", "status", "external_ids"}
    )

    def normalize(self, raw: OpenLibraryRawData) -> list[NormalizedItem]:
        items: list[NormalizedItem] = []
        seen: set[str] = set()
        for shelf, entries in raw.shelves.items():
            status = _SHELF_MAP.get(shelf)
            if status is None:
                continue
            for entry in entries:
                item = self._normalize_entry(entry, shelf, status)
                if item is None:
                    continue
                work_key = item.work.external_ids.get("openlibrary", "")
                if work_key in seen:
                    continue
                seen.add(work_key)
                items.append(item)
        return items

    def _normalize_entry(
        self, entry: dict[str, Any], shelf: str, status: ItemStatus
    ) -> NormalizedItem | None:
        work = entry.get("work") or {}
        title = str(work.get("title", "")).strip()
        if not title:
            return None
        authors = [
            str(name).strip() for name in work.get("author_names", []) if str(name).strip()
        ]
        year = work.get("first_publish_year")
        logged_at = self._parse_logged(entry.get("logged_date"))
        work_key = str(work.get("key", "")).removeprefix("/works/")
        return NormalizedItem(
            work=Work(
                title=title,
                creators=authors,
                year=int(year) if year else None,
                external_ids={"openlibrary": work_key} if work_key else {},
                extra={"shelf": shelf},
            ),
            category=Category.books,
            status=status,
            added_at=logged_at,
            finished_at=logged_at if status is ItemStatus.consumed else None,
            engagement={"pages": 0, "read_count": 1 if status is ItemStatus.consumed else 0},
            source=self.id,
            provenance={"title": self.id, "status": self.id},
        )

    @staticmethod
    def _parse_logged(value: object) -> datetime | None:
        # Formato de la API: "2021/03/23, 15:31:35".
        if not value:
            return None
        try:
            return datetime.strptime(str(value), "%Y/%m/%d, %H:%M:%S").replace(tzinfo=UTC)
        except ValueError:
            return None
