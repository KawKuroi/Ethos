"""Generador del resumen de Libros desde los registros normalizados (D48)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime

from pydantic import BaseModel

from ethos_api.schema import ItemStatus, NormalizedItem


class TopAuthor(BaseModel):
    """Autor con más libros leídos."""

    name: str
    books: int


class CurrentBook(BaseModel):
    """Libro en curso de lectura."""

    title: str
    author: str


class RecentRead(BaseModel):
    """Lectura terminada recientemente, con la nota si la hay (0-100)."""

    title: str
    author: str
    finished_at: datetime | None = None
    rating: int | None = None


class BooksSummary(BaseModel):
    """Resumen agregado del gusto en Libros (base del resource MCP y la web)."""

    books_read: int
    pages_read: int
    currently_reading: list[CurrentBook]
    wishlisted: int
    top_authors: list[TopAuthor]
    recent_reads: list[RecentRead]
    last_synced_at: datetime | None = None


def _author(item: NormalizedItem) -> str:
    return item.work.creators[0] if item.work.creators else ""


def build_books_summary(
    items: list[NormalizedItem],
    *,
    synced_at: datetime | None = None,
    top_limit: int = 10,
) -> BooksSummary:
    """Agrega los libros en el resumen: leídos, páginas, en curso, autores."""
    read = [i for i in items if i.status is ItemStatus.consumed]
    reading = [i for i in items if i.status is ItemStatus.in_progress]
    wishlisted = sum(1 for i in items if i.status is ItemStatus.wishlist)

    author_counts: Counter[str] = Counter(
        author for i in read if (author := _author(i))
    )
    top_authors = [
        TopAuthor(name=name, books=count)
        for name, count in author_counts.most_common(top_limit)
    ]

    with_date = [i for i in read if i.finished_at is not None]
    with_date.sort(key=lambda i: i.finished_at or datetime.min, reverse=True)
    recent_reads = [
        RecentRead(
            title=i.work.title,
            author=_author(i),
            finished_at=i.finished_at,
            rating=i.rating_normalized,
        )
        for i in with_date[:top_limit]
    ]

    return BooksSummary(
        books_read=len(read),
        pages_read=sum(i.engagement.get("pages", 0) for i in read),
        currently_reading=[
            CurrentBook(title=i.work.title, author=_author(i)) for i in reading
        ],
        wishlisted=wishlisted,
        top_authors=top_authors,
        recent_reads=recent_reads,
        last_synced_at=synced_at,
    )
