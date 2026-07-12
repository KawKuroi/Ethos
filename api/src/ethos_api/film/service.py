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
from ethos_api.schema import NormalizedItem
from ethos_api.sources_status import SourceStatus, SyncState

# Códigos de Trakt que indican perfil no accesible (privado o inexistente).
_NOT_ACCESSIBLE = frozenset({401, 403, 404})


class TraktApi(Protocol):
    """Superficie del cliente de Trakt que usa el refresco (testeable)."""

    def get_user_stats(self, user_name: str) -> dict[str, Any]: ...

    def get_watched_movies(self, user_name: str) -> list[dict[str, Any]]: ...

    def get_watched_shows(self, user_name: str) -> list[dict[str, Any]]: ...


def _trakt_status(
    state: SyncState,
    *,
    synced_at: datetime | None = None,
    detail: str | None = None,
) -> SourceStatus:
    return SourceStatus(
        state=state,
        synced_at=synced_at,
        detail=detail,
        provider="trakt",
        mode="api",
    )


def refresh_user_film(
    user_id: str,
    user_name: str,
    client: TraktApi,
    store: FilmStore,
) -> None:
    """Sincroniza lo visto de un usuario y deja el estado de frescura."""
    store.set_status(user_id, _trakt_status(SyncState.syncing))
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
            user_id, _trakt_status(SyncState.fresh, synced_at=datetime.now(UTC))
        )
    except TraktApiError as error:
        if error.status_code in _NOT_ACCESSIBLE:
            store.replace_items(user_id, [])
            store.set_status(
                user_id,
                _trakt_status(
                    SyncState.private,
                    detail=(
                        "Tu perfil de Trakt es privado o el usuario no existe; "
                        "ponlo en público y vuelve a refrescar"
                    ),
                ),
            )
        else:
            store.set_status(
                user_id, _trakt_status(SyncState.error, detail=str(error))
            )
    except Exception as error:  # el estado reporta el fallo, no se propaga
        store.set_status(user_id, _trakt_status(SyncState.error, detail=str(error)))


def import_film_items(
    user_id: str,
    provider: str,
    items: list[NormalizedItem],
    store: FilmStore,
) -> int:
    """Importa obras de un export y devuelve cuántas quedaron guardadas.

    Si el proveedor coincide con la fuente actual, combina por id externo
    (el export de Letterboxd llega en varios CSV: watched, diary, ratings);
    si es otro proveedor, reemplaza (D4). Los agregados del proveedor
    anterior (horas de Trakt) se limpian: un import no los trae.
    """
    current = store.status_for_user(user_id)
    merged: dict[str, NormalizedItem] = {}
    if current.provider == provider:
        for item in store.items_for_user(user_id):
            if item.source == "manual":
                continue  # las entradas a mano las conserva replace_items
            merged[_film_key(item)] = item
    for item in items:
        key = _film_key(item)
        existing = merged.get(key)
        merged[key] = item if existing is None else _merge_film(existing, item)
    store.replace_items(user_id, list(merged.values()))
    store.set_stats(user_id, None)
    store.set_status(
        user_id,
        SourceStatus(
            state=SyncState.fresh,
            synced_at=datetime.now(UTC),
            provider=provider,
            mode="import",
        ),
    )
    return len(merged)


def _film_key(item: NormalizedItem) -> str:
    ids = item.work.external_ids
    return ids.get(item.source) or next(iter(ids.values()), item.work.title)


def _merge_film(existing: NormalizedItem, new: NormalizedItem) -> NormalizedItem:
    """Combina la misma obra venida de dos CSV: lo nuevo manda, sin perder datos."""
    merged = new.model_copy(deep=True)
    if merged.rating_normalized is None:
        merged.rating_normalized = existing.rating_normalized
        merged.rating_original = existing.rating_original
    if merged.finished_at is None:
        merged.finished_at = existing.finished_at
    if merged.engagement.get("plays", 0) < existing.engagement.get("plays", 0):
        merged.engagement["plays"] = existing.engagement["plays"]
    if "last_watched_at" not in merged.work.extra and "last_watched_at" in existing.work.extra:
        merged.work.extra["last_watched_at"] = existing.work.extra["last_watched_at"]
    return merged
