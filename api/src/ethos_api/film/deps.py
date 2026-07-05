"""Dependencias del slice de Cine y TV (singletons y factorías inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.config import settings
from ethos_api.connectors.trakt.client import TraktApiClient
from ethos_api.film.service import TraktApi
from ethos_api.film.store import FilmStore, InMemoryFilmStore, SupabaseFilmStore
from ethos_api.supabase_rest import get_rest

_store: FilmStore | None = None


def get_film_store() -> FilmStore:
    """Supabase si está configurado; memoria en local/CI (D42)."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseFilmStore(rest) if rest else InMemoryFilmStore()
    return _store


def get_trakt_client() -> TraktApi:
    """Cliente real de Trakt; los tests lo sustituyen con un fake."""
    return TraktApiClient(settings.trakt_client_id.get_secret_value())


FilmStoreDep = Annotated[FilmStore, Depends(get_film_store)]
TraktClientDep = Annotated[TraktApi, Depends(get_trakt_client)]
