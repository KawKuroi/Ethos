"""Endpoint del import genérico: autodetecta el proveedor y delega (D49/D62)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from ethos_api.auth import CurrentUserId
from ethos_api.books.deps import BooksStoreDep
from ethos_api.books.service import import_goodreads_csv, import_storygraph_csv
from ethos_api.connectors.applemusic.connector import (
    AppleMusicConnector,
    AppleMusicImportError,
    AppleMusicRawData,
)
from ethos_api.connectors.goodreads.connector import GoodreadsImportError
from ethos_api.connectors.imdb.connector import (
    ImdbConnector,
    ImdbImportError,
    ImdbRawData,
)
from ethos_api.connectors.letterboxd.connector import (
    LetterboxdConnector,
    LetterboxdImportError,
    LetterboxdRawData,
)
from ethos_api.connectors.registry import registry
from ethos_api.connectors.spotify.connector import (
    SpotifyConnector,
    SpotifyImportError,
    SpotifyRawData,
)
from ethos_api.connectors.storygraph.connector import StorygraphImportError
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.film.deps import FilmStoreDep
from ethos_api.film.service import import_film_items
from ethos_api.imports.detection import detect_import
from ethos_api.music.deps import EventStoreDep
from ethos_api.music.service import import_music_events

router = APIRouter(tags=["imports"])

_UNRECOGNIZED = (
    "No reconocimos el archivo. Sube el export original de tu proveedor: "
    "Goodreads o StoryGraph (CSV de biblioteca), Letterboxd (diary, watched "
    "o ratings CSV), IMDb (ratings CSV), Spotify (Streaming_History_*.json) "
    "o Apple Music (Play History Daily Tracks CSV)."
)

_IMPORT_ERRORS = (
    GoodreadsImportError,
    StorygraphImportError,
    LetterboxdImportError,
    ImdbImportError,
    SpotifyImportError,
    AppleMusicImportError,
)


@router.post("/imports", status_code=status.HTTP_201_CREATED)
async def generic_import(
    request: Request,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    books_store: BooksStoreDep,
    film_store: FilmStoreDep,
    event_store: EventStoreDep,
) -> dict[str, object]:
    """Detecta el proveedor por la firma del archivo y ejecuta su import."""
    body = await request.body()
    text = body.decode("utf-8-sig", errors="replace")
    signature = detect_import(text)
    if signature is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=_UNRECOGNIZED
        )
    try:
        # Despacho por proveedor detectado: cada flujo normaliza y persiste.
        if signature.provider == "goodreads":
            imported = import_goodreads_csv(user_id, text, books_store)
        elif signature.provider == "storygraph":
            imported = import_storygraph_csv(user_id, text, books_store)
        elif signature.provider == "letterboxd":
            items = LetterboxdConnector().normalize(LetterboxdRawData(csv_text=text))
            imported = import_film_items(user_id, "letterboxd", items, film_store)
        elif signature.provider == "imdb":
            items = ImdbConnector().normalize(ImdbRawData(csv_text=text))
            imported = import_film_items(user_id, "imdb", items, film_store)
        elif signature.provider == "spotify":
            events = SpotifyConnector().normalize(SpotifyRawData(json_text=text))
            imported = import_music_events(user_id, "spotify", events, event_store)
        elif signature.provider == "applemusic":
            events = AppleMusicConnector().normalize(AppleMusicRawData(csv_text=text))
            imported = import_music_events(user_id, "applemusic", events, event_store)
        else:  # firma registrada sin flujo: error de programación
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=_UNRECOGNIZED
            )
    except _IMPORT_ERRORS as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    # Una sola fuente activa por categoría (D4): el import desconecta a los
    # proveedores API de la categoría (sus credenciales dejan de aplicar).
    for sibling in registry.providers(signature.category):
        repo.delete(user_id, sibling)
    return {
        "provider": signature.provider,
        "category": signature.category.value,
        "status": "imported",
        "items": imported,
    }
