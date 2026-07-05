"""Contexto descargable de Libros: `books.context.json` (D24/D48)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.books.summary import BooksSummary


def build_books_context(summary: BooksSummary) -> dict[str, object]:
    """Arma el contexto de Libros (misma información que sirve el MCP)."""
    return {
        "namespace": "books.*",
        "provider": "goodreads",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "books_read": summary.books_read,
            "pages_read": summary.pages_read,
            "wishlisted": summary.wishlisted,
            "last_synced_at": (
                summary.last_synced_at.isoformat() if summary.last_synced_at else None
            ),
        },
        "currently_reading": [
            c.model_dump(mode="json") for c in summary.currently_reading
        ],
        "top_authors": [a.model_dump(mode="json") for a in summary.top_authors],
        "recent_reads": [r.model_dump(mode="json") for r in summary.recent_reads],
    }
