"""Import de la fuente de Libros: parsear el CSV → normalizar → persistir (D47).

A diferencia de las fuentes API, el import es síncrono (el archivo ya está en
la petición) y reemplaza el conjunto completo: el "refresco" de un import es
volver a subir el export. Lo reutiliza el endpoint del proveedor y el import
genérico con autodetección (D49).
"""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.books.store import BooksStore
from ethos_api.connectors.goodreads.connector import GoodreadsConnector, GoodreadsRawData
from ethos_api.sources_status import SourceStatus, SyncState


def import_goodreads_csv(user_id: str, csv_text: str, store: BooksStore) -> int:
    """Importa el export de Goodreads y devuelve cuántos libros normalizó.

    Lanza `GoodreadsImportError` si el archivo no es un export válido; en ese
    caso no toca los datos existentes del usuario.
    """
    connector = GoodreadsConnector()
    items = connector.normalize(GoodreadsRawData(csv_text=csv_text))
    store.replace_items(user_id, items)
    store.set_status(
        user_id, SourceStatus(state=SyncState.fresh, synced_at=datetime.now(UTC))
    )
    return len(items)
