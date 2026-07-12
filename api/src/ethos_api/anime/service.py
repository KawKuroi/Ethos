"""Refresco de la fuente de Anime y manga: fetch → normalizar → persistir.

Corre en segundo plano (BackgroundTasks). Los tres proveedores (AniList D45,
MyAnimeList y Kitsu D62) entregan las listas completas ya agregadas, así que
el refresco reemplaza el conjunto por pasada (idempotente, como Cine y TV,
D44). Un usuario inexistente o con listas privadas deja estado `private` con
guía para la web.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.anime.store import AnimeStore
from ethos_api.connectors.anilist.client import AniListApiError
from ethos_api.connectors.anilist.connector import AniListConnector, AniListRawData
from ethos_api.connectors.kitsu.client import KitsuApiError
from ethos_api.connectors.kitsu.connector import KitsuConnector, KitsuRawData
from ethos_api.connectors.mal.client import MalApiError
from ethos_api.connectors.mal.connector import MalConnector, MalRawData
from ethos_api.schema import NormalizedItem
from ethos_api.sources_status import SourceStatus, SyncState

# Códigos que indican perfil no accesible (privado o inexistente).
_NOT_ACCESSIBLE = frozenset({401, 403, 404})
_PROVIDER_ERRORS = (AniListApiError, MalApiError, KitsuApiError)


class AniListApi(Protocol):
    """Superficie del cliente de AniList que usa el refresco (testeable)."""

    def get_media_lists(self, user_name: str) -> dict[str, Any]: ...


class MalApi(Protocol):
    """Superficie del cliente de MyAnimeList que usa el refresco (testeable)."""

    def get_anime_list(self, user_name: str) -> list[dict[str, Any]]: ...

    def get_manga_list(self, user_name: str) -> list[dict[str, Any]]: ...


class KitsuApi(Protocol):
    """Superficie del cliente de Kitsu que usa el refresco (testeable)."""

    def find_user_id(self, user_name: str) -> str: ...

    def get_library(self, user_id: str, kind: str) -> dict[str, Any]: ...


def _lists(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    collection = data.get(key) or {}
    lists = collection.get("lists")
    return lists if isinstance(lists, list) else []


def _run_refresh(
    user_id: str,
    store: AnimeStore,
    provider: str,
    fetch: Callable[[], list[NormalizedItem]],
    private_detail: str,
) -> None:
    """Ciclo común del refresco: estados de frescura + reemplazo por pasada."""
    store.set_status(
        user_id, SourceStatus(state=SyncState.syncing, provider=provider, mode="api")
    )
    try:
        store.replace_items(user_id, fetch())
        store.set_status(
            user_id,
            SourceStatus(
                state=SyncState.fresh,
                synced_at=datetime.now(UTC),
                provider=provider,
                mode="api",
            ),
        )
    except _PROVIDER_ERRORS as error:
        if error.status_code in _NOT_ACCESSIBLE:
            store.replace_items(user_id, [])
            store.set_status(
                user_id,
                SourceStatus(
                    state=SyncState.private,
                    detail=private_detail,
                    provider=provider,
                    mode="api",
                ),
            )
        else:
            store.set_status(
                user_id,
                SourceStatus(
                    state=SyncState.error,
                    detail=str(error),
                    provider=provider,
                    mode="api",
                ),
            )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        store.set_status(
            user_id,
            SourceStatus(
                state=SyncState.error, detail=str(error), provider=provider, mode="api"
            ),
        )


def refresh_user_anime(
    user_id: str,
    user_name: str,
    client: AniListApi,
    store: AnimeStore,
) -> None:
    """Sincroniza las listas de AniList de un usuario (D45)."""

    def fetch() -> list[NormalizedItem]:
        data = client.get_media_lists(user_name)
        raw = AniListRawData(
            anime_lists=_lists(data, "anime"),
            manga_lists=_lists(data, "manga"),
        )
        return AniListConnector().normalize(raw)

    _run_refresh(
        user_id,
        store,
        "anilist",
        fetch,
        "Tu usuario de AniList no existe o sus listas son privadas; "
        "revísalo y vuelve a conectar",
    )


def refresh_user_anime_mal(
    user_id: str,
    user_name: str,
    client: MalApi,
    store: AnimeStore,
) -> None:
    """Sincroniza las listas públicas de MyAnimeList de un usuario (D62)."""

    def fetch() -> list[NormalizedItem]:
        raw = MalRawData(
            anime_entries=client.get_anime_list(user_name),
            manga_entries=client.get_manga_list(user_name),
        )
        return MalConnector().normalize(raw)

    _run_refresh(
        user_id,
        store,
        "mal",
        fetch,
        "Tu usuario de MyAnimeList no existe o su lista es privada; "
        "revísalo y vuelve a conectar",
    )


def refresh_user_anime_kitsu(
    user_id: str,
    user_name: str,
    client: KitsuApi,
    store: AnimeStore,
) -> None:
    """Sincroniza la biblioteca pública de Kitsu de un usuario (D62)."""

    def fetch() -> list[NormalizedItem]:
        kitsu_user_id = client.find_user_id(user_name)
        raw = KitsuRawData(
            anime_library=client.get_library(kitsu_user_id, "anime"),
            manga_library=client.get_library(kitsu_user_id, "manga"),
        )
        return KitsuConnector().normalize(raw)

    _run_refresh(
        user_id,
        store,
        "kitsu",
        fetch,
        "Tu usuario de Kitsu no existe o su biblioteca es privada; "
        "revísalo y vuelve a conectar",
    )
