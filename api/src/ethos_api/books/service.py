"""Import y refresco de la fuente de Libros (D47/D62).

Import (Goodreads D47, StoryGraph D62): síncrono (el archivo ya está en la
petición) y reemplaza el conjunto completo — el "refresco" de un import es
volver a subir el export. API (Open Library, Hardcover, D62): refresco en
segundo plano que reemplaza por pasada, como Anime (D44/D46).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Protocol

from ethos_api.books.store import BooksStore
from ethos_api.connectors.goodreads.connector import GoodreadsConnector, GoodreadsRawData
from ethos_api.connectors.hardcover.client import HardcoverApiError
from ethos_api.connectors.hardcover.connector import HardcoverConnector, HardcoverRawData
from ethos_api.connectors.openlibrary.client import SHELVES, OpenLibraryApiError
from ethos_api.connectors.openlibrary.connector import (
    OpenLibraryConnector,
    OpenLibraryRawData,
)
from ethos_api.connectors.storygraph.connector import (
    StorygraphConnector,
    StorygraphRawData,
)
from ethos_api.schema import NormalizedItem
from ethos_api.sources_status import SourceStatus, SyncState

# Códigos que indican fuente no accesible (privada, inexistente o token caído).
_NOT_ACCESSIBLE = frozenset({401, 403, 404})
_PROVIDER_ERRORS = (OpenLibraryApiError, HardcoverApiError)


class OpenLibraryApi(Protocol):
    """Superficie del cliente de Open Library que usa el refresco (testeable)."""

    def get_shelf(self, user_name: str, shelf: str) -> list[dict[str, Any]]: ...


class HardcoverApi(Protocol):
    """Superficie del cliente de Hardcover que usa el refresco (testeable)."""

    def get_user_books(self, token: str) -> list[dict[str, Any]]: ...


def import_goodreads_csv(user_id: str, csv_text: str, store: BooksStore) -> int:
    """Importa el export de Goodreads y devuelve cuántos libros normalizó.

    Lanza `GoodreadsImportError` si el archivo no es un export válido; en ese
    caso no toca los datos existentes del usuario.
    """
    connector = GoodreadsConnector()
    items = connector.normalize(GoodreadsRawData(csv_text=csv_text))
    _finish_import(store, user_id, "goodreads", items)
    return len(items)


def import_storygraph_csv(user_id: str, csv_text: str, store: BooksStore) -> int:
    """Importa el export de StoryGraph y devuelve cuántos libros normalizó.

    Lanza `StorygraphImportError` si el archivo no es un export válido; en ese
    caso no toca los datos existentes del usuario.
    """
    connector = StorygraphConnector()
    items = connector.normalize(StorygraphRawData(csv_text=csv_text))
    _finish_import(store, user_id, "storygraph", items)
    return len(items)


def refresh_user_books_openlibrary(
    user_id: str,
    user_name: str,
    client: OpenLibraryApi,
    store: BooksStore,
) -> None:
    """Sincroniza el reading log público de Open Library de un usuario (D62)."""

    def fetch() -> list[NormalizedItem]:
        shelves = {shelf: client.get_shelf(user_name, shelf) for shelf in SHELVES}
        return OpenLibraryConnector().normalize(OpenLibraryRawData(shelves=shelves))

    _run_refresh(
        user_id,
        store,
        "openlibrary",
        fetch,
        "Tu usuario de Open Library no existe o su reading log es privado; "
        "hazlo público en Settings → Privacy y vuelve a conectar",
    )


def refresh_user_books_hardcover(
    user_id: str,
    token: str,
    client: HardcoverApi,
    store: BooksStore,
) -> None:
    """Sincroniza la biblioteca de Hardcover con el token del usuario (D62)."""

    def fetch() -> list[NormalizedItem]:
        books = client.get_user_books(token)
        return HardcoverConnector().normalize(HardcoverRawData(user_books=books))

    _run_refresh(
        user_id,
        store,
        "hardcover",
        fetch,
        "Tu token de Hardcover no es válido o caducó (expira cada año); "
        "genera uno nuevo en hardcover.app → Settings → Hardcover API",
    )


def _finish_import(
    store: BooksStore, user_id: str, provider: str, items: list[NormalizedItem]
) -> None:
    store.replace_items(user_id, items)
    store.set_status(
        user_id,
        SourceStatus(
            state=SyncState.fresh,
            synced_at=datetime.now(UTC),
            provider=provider,
            mode="import",
        ),
    )


def _run_refresh(
    user_id: str,
    store: BooksStore,
    provider: str,
    fetch: Callable[[], list[NormalizedItem]],
    private_detail: str,
) -> None:
    """Ciclo común del refresco API: estados de frescura + reemplazo por pasada."""
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
