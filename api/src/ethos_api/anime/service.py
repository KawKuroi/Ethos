"""Refresco de la fuente de Anime y manga: fetch → normalizar → persistir (D45).

Corre en segundo plano (BackgroundTasks). AniList entrega las listas completas
ya agregadas, así que el refresco reemplaza el conjunto por pasada
(idempotente, como Cine y TV, D44). Un usuario inexistente o con listas
privadas (404) deja estado `private` con guía para la web.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.anime.store import AnimeStore
from ethos_api.connectors.anilist.client import AniListApiError
from ethos_api.connectors.anilist.connector import AniListConnector, AniListRawData
from ethos_api.sources_status import SourceStatus, SyncState

# Códigos de AniList que indican perfil no accesible (privado o inexistente).
_NOT_ACCESSIBLE = frozenset({401, 403, 404})


class AniListApi(Protocol):
    """Superficie del cliente de AniList que usa el refresco (testeable)."""

    def get_media_lists(self, user_name: str) -> dict[str, Any]: ...


def _lists(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    collection = data.get(key) or {}
    lists = collection.get("lists")
    return lists if isinstance(lists, list) else []


def refresh_user_anime(
    user_id: str,
    user_name: str,
    client: AniListApi,
    store: AnimeStore,
) -> None:
    """Sincroniza las listas de un usuario y deja el estado de frescura."""
    store.set_status(user_id, SourceStatus(state=SyncState.syncing))
    connector = AniListConnector()
    try:
        data = client.get_media_lists(user_name)
        raw = AniListRawData(
            anime_lists=_lists(data, "anime"),
            manga_lists=_lists(data, "manga"),
        )
        store.replace_items(user_id, connector.normalize(raw))
        store.set_status(
            user_id, SourceStatus(state=SyncState.fresh, synced_at=datetime.now(UTC))
        )
    except AniListApiError as error:
        if error.status_code in _NOT_ACCESSIBLE:
            store.replace_items(user_id, [])
            store.set_status(
                user_id,
                SourceStatus(
                    state=SyncState.private,
                    detail=(
                        "Tu usuario de AniList no existe o sus listas son privadas; "
                        "revísalo y vuelve a conectar"
                    ),
                ),
            )
        else:
            store.set_status(
                user_id, SourceStatus(state=SyncState.error, detail=str(error))
            )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        store.set_status(
            user_id, SourceStatus(state=SyncState.error, detail=str(error))
        )
