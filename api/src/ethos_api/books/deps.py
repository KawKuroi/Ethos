"""Dependencias del slice de Libros (singletons inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.books.service import HardcoverApi, OpenLibraryApi
from ethos_api.books.store import BooksStore, InMemoryBooksStore, SupabaseBooksStore
from ethos_api.connectors.hardcover.client import HardcoverClient
from ethos_api.connectors.openlibrary.client import OpenLibraryClient
from ethos_api.supabase_rest import get_rest

_store: BooksStore | None = None


def get_books_store() -> BooksStore:
    """Supabase si está configurado; memoria en local/CI (D47)."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseBooksStore(rest) if rest else InMemoryBooksStore()
    return _store


def get_openlibrary_client() -> OpenLibraryApi:
    """Cliente real de Open Library (sin key, D62); los tests lo sustituyen."""
    return OpenLibraryClient()


def get_hardcover_client() -> HardcoverApi:
    """Cliente real de Hardcover (token por usuario, D62)."""
    return HardcoverClient()


BooksStoreDep = Annotated[BooksStore, Depends(get_books_store)]
OpenLibraryClientDep = Annotated[OpenLibraryApi, Depends(get_openlibrary_client)]
HardcoverClientDep = Annotated[HardcoverApi, Depends(get_hardcover_client)]
