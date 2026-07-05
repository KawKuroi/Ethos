"""Dependencias del slice de Anime y manga (singletons y factorías inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.anime.service import AniListApi
from ethos_api.anime.store import AnimeStore, InMemoryAnimeStore, SupabaseAnimeStore
from ethos_api.connectors.anilist.client import AniListApiClient
from ethos_api.supabase_rest import get_rest

_store: AnimeStore | None = None


def get_anime_store() -> AnimeStore:
    """Supabase si está configurado; memoria en local/CI (D46)."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseAnimeStore(rest) if rest else InMemoryAnimeStore()
    return _store


def get_anilist_client() -> AniListApi:
    """Cliente real de AniList (sin key, D45); los tests lo sustituyen."""
    return AniListApiClient()


AnimeStoreDep = Annotated[AnimeStore, Depends(get_anime_store)]
AniListClientDep = Annotated[AniListApi, Depends(get_anilist_client)]
