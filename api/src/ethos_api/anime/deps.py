"""Dependencias del slice de Anime y manga (singletons y factorías inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.anime.service import AniListApi, KitsuApi, MalApi
from ethos_api.anime.store import AnimeStore, InMemoryAnimeStore, SupabaseAnimeStore
from ethos_api.config import settings
from ethos_api.connectors.anilist.client import AniListApiClient
from ethos_api.connectors.kitsu.client import KitsuClient
from ethos_api.connectors.mal.client import MalClient
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


def get_mal_client() -> MalApi:
    """Cliente real de MyAnimeList (client id de config, D62)."""
    return MalClient(settings.mal_client_id.get_secret_value())


def get_kitsu_client() -> KitsuApi:
    """Cliente real de Kitsu (sin key, D62); los tests lo sustituyen."""
    return KitsuClient()


AnimeStoreDep = Annotated[AnimeStore, Depends(get_anime_store)]
AniListClientDep = Annotated[AniListApi, Depends(get_anilist_client)]
MalClientDep = Annotated[MalApi, Depends(get_mal_client)]
KitsuClientDep = Annotated[KitsuApi, Depends(get_kitsu_client)]
