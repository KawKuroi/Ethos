"""Generador del resumen de Libros desde los registros normalizados (D48)."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

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


class LongestBook(BaseModel):
    """El libro leído más largo (solo si la fuente trae páginas)."""

    title: str
    pages: int


class BooksSummary(BaseModel):
    """Resumen agregado del gusto en Libros (base del resource MCP y la web).

    Nota media, relecturas y páginas dependen de la fuente (Goodreads y
    Hardcover traen páginas; StoryGraph y Open Library no): la web oculta
    lo que quede a cero o en None.
    """

    books_read: int
    pages_read: int
    currently_reading: list[CurrentBook]
    wishlisted: int
    top_authors: list[TopAuthor]
    recent_reads: list[RecentRead]
    # Notas del usuario (0-100 normalizado).
    mean_rating: float | None = None
    rated_count: int = 0
    # Libros con más de una lectura registrada.
    rereads: int = 0
    # Terminados en el año natural en curso.
    books_this_year: int = 0
    longest_book: LongestBook | None = None
    avg_pages: int | None = None
    last_synced_at: datetime | None = None


def _author(item: NormalizedItem) -> str:
    return item.work.creators[0] if item.work.creators else ""


def build_books_summary(
    items: list[NormalizedItem],
    *,
    synced_at: datetime | None = None,
    now: datetime | None = None,
    top_limit: int = 10,
) -> BooksSummary:
    """Agrega los libros en el resumen: leídos, páginas, en curso, autores."""
    now = now or datetime.now(UTC)
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

    rated = [i for i in read if i.rating_normalized is not None]
    mean_rating = (
        round(sum(i.rating_normalized or 0 for i in rated) / len(rated), 1)
        if rated
        else None
    )

    with_pages = [i for i in read if i.engagement.get("pages", 0) > 0]
    longest = max(with_pages, key=lambda i: i.engagement.get("pages", 0), default=None)

    return BooksSummary(
        books_read=len(read),
        pages_read=sum(i.engagement.get("pages", 0) for i in read),
        currently_reading=[
            CurrentBook(title=i.work.title, author=_author(i)) for i in reading
        ],
        wishlisted=wishlisted,
        top_authors=top_authors,
        recent_reads=recent_reads,
        mean_rating=mean_rating,
        rated_count=len(rated),
        rereads=sum(1 for i in read if i.engagement.get("read_count", 0) > 1),
        books_this_year=sum(
            1 for i in read if i.finished_at is not None and i.finished_at.year == now.year
        ),
        longest_book=(
            LongestBook(title=longest.work.title, pages=longest.engagement.get("pages", 0))
            if longest is not None
            else None
        ),
        avg_pages=(
            round(
                sum(i.engagement.get("pages", 0) for i in with_pages) / len(with_pages)
            )
            if with_pages
            else None
        ),
        last_synced_at=synced_at,
    )
