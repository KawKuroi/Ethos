"""Dependencias del slice de Libros (singletons inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.books.store import BooksStore, InMemoryBooksStore, SupabaseBooksStore
from ethos_api.supabase_rest import get_rest

_store: BooksStore | None = None


def get_books_store() -> BooksStore:
    """Supabase si está configurado; memoria en local/CI (D47)."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseBooksStore(rest) if rest else InMemoryBooksStore()
    return _store


BooksStoreDep = Annotated[BooksStore, Depends(get_books_store)]
