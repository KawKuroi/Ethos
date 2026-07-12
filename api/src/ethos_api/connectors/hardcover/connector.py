"""Conector de Hardcover: normaliza `user_books` al contrato común (D62).

Misma forma que Goodreads (D47): autor en `creators`, páginas en `engagement`,
rating 0-5 (con medios) → 0-100 y fechas de la biblioteca.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# status_id de Hardcover → vocabulario común.
# 1 Want to Read · 2 Currently Reading · 3 Read · 4 Paused · 5 DNF · 6 Ignored.
_STATUS_MAP = {
    1: ItemStatus.wishlist,
    2: ItemStatus.in_progress,
    3: ItemStatus.consumed,
    4: ItemStatus.in_progress,
    5: ItemStatus.abandoned,
}


@dataclass
class HardcoverRawData:
    """`user_books` crudos de la API GraphQL."""

    user_books: list[dict[str, Any]] = field(default_factory=list)


class HardcoverConnector(Connector[HardcoverRawData, NormalizedItem]):
    """Conector del proveedor Hardcover (categoría Libros, API)."""

    id: ClassVar[str] = "hardcover"
    category: ClassVar[Category] = Category.books
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "creators", "status", "rating", "review", "engagement"}
    )

    def normalize(self, raw: HardcoverRawData) -> list[NormalizedItem]:
        items: list[NormalizedItem] = []
        seen: set[str] = set()
        for user_book in raw.user_books:
            item = self._normalize_book(user_book)
            if item is None:
                continue
            book_id = item.work.external_ids.get("hardcover", "")
            if book_id in seen:
                continue
            seen.add(book_id)
            items.append(item)
        return items

    def _normalize_book(self, user_book: dict[str, Any]) -> NormalizedItem | None:
        book = user_book.get("book") or {}
        title = str(book.get("title", "")).strip()
        if not title:
            return None
        status_id = user_book.get("status_id")
        status = _STATUS_MAP.get(int(status_id) if status_id else 0, ItemStatus.in_library)
        authors = [
            str(((contribution or {}).get("author") or {}).get("name", "")).strip()
            for contribution in book.get("contributions", [])
        ]
        authors = [author for author in authors if author]
        # Rating 0-5 con medios (3.5) → 0-100; None/0 = sin puntuar.
        rating_raw = user_book.get("rating")
        rating = round(float(rating_raw) * 20) if rating_raw else None
        pages = int(book.get("pages") or 0)
        review = str(user_book.get("review") or "").strip()
        year = book.get("release_year")
        return NormalizedItem(
            work=Work(
                title=title,
                creators=authors,
                year=int(year) if year else None,
                external_ids={"hardcover": str(user_book.get("book_id", ""))},
            ),
            category=Category.books,
            status=status,
            rating_normalized=rating,
            rating_original=str(rating_raw) if rating_raw else None,
            added_at=self._parse_date(user_book.get("date_added")),
            finished_at=self._parse_date(user_book.get("last_read_date")),
            engagement={
                "pages": pages,
                "read_count": 1 if status is ItemStatus.consumed else 0,
            },
            review=review or None,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "rating": self.id},
        )

    @staticmethod
    def _parse_date(value: object) -> datetime | None:
        # Fechas de Hardcover: "2026-01-15" o ISO 8601 completo.
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
