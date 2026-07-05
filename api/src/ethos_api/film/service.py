"""Refresco de la fuente de Cine y TV: fetch → normalizar → persistir (D44).

Corre en segundo plano (BackgroundTasks). Trakt entrega lo visto ya agregado,
así que el refresco reemplaza el conjunto completo por pasada (idempotente,
como Juegos); no es incremental. Un perfil privado o un usuario inexistente
(401/403/404) deja estado `private` con guía para la web.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.connectors.trakt.client import TraktApiError
from ethos_api.connectors.trakt.connector import TraktConnector, TraktRawData
from ethos_api.film.store import FilmStore
from ethos_api.sources_status import SourceStatus, SyncState

# Códigos de Trakt que indican perfil no accesible (privado o inexistente).
_NOT_ACCESSIBLE = frozenset({401, 403, 404})


class TraktApi(Protocol):
    """Superficie del cliente de Trakt que usa el refresco (testeable)."""

    def get_user_stats(self, user_name: str) -> dict[str, Any]: ...

    def get_watched_movies(self, user_name: str) -> list[dict[str, Any]]: ...

    def get_watched_shows(self, user_name: str) -> list[dict[str, Any]]: ...


def refresh_user_film(
    user_id: str,
    user_name: str,
    client: TraktApi,
    store: FilmStore,
) -> None:
    """Sincroniza lo visto de un usuario y deja el estado de frescura."""
    store.set_status(user_id, SourceStatus(state=SyncState.syncing))
    connector = TraktConnector()
    try:
        raw = TraktRawData(
            watched_movies=client.get_watched_movies(user_name),
            watched_shows=client.get_watched_shows(user_name),
            stats=client.get_user_stats(user_name),
        )
        store.replace_items(user_id, connector.normalize(raw))
        store.set_stats(user_id, connector.stats(raw))
        store.set_status(
            user_id, SourceStatus(state=SyncState.fresh, synced_at=datetime.now(UTC))
        )
    except TraktApiError as error:
        if error.status_code in _NOT_ACCESSIBLE:
            store.replace_items(user_id, [])
            store.set_status(
                user_id,
                SourceStatus(
                    state=SyncState.private,
                    detail=(
                        "Tu perfil de Trakt es privado o el usuario no existe; "
                        "ponlo en público y vuelve a refrescar"
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
