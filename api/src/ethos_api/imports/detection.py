"""Autodetección del proveedor de un archivo de import (D49/D62).

Cada proveedor de import declara una firma: para un CSV, las cabeceras que
identifican su export; para un JSON (Spotify), la forma de sus registros. La
detección prueba las firmas en orden (la más específica primero) y devuelve
la primera que encaja. Añadir un proveedor de import es registrar aquí su
firma y su flujo en el router de imports.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field

from ethos_api.connectors.applemusic.connector import (
    REQUIRED_COLUMNS as APPLEMUSIC_COLUMNS,
)
from ethos_api.connectors.goodreads.connector import (
    REQUIRED_COLUMNS as GOODREADS_COLUMNS,
)
from ethos_api.connectors.imdb.connector import REQUIRED_COLUMNS as IMDB_COLUMNS
from ethos_api.connectors.letterboxd.connector import (
    DIARY_COLUMNS,
    RATINGS_COLUMNS,
    WATCHED_COLUMNS,
)
from ethos_api.connectors.spotify.connector import looks_like_spotify
from ethos_api.connectors.storygraph.connector import (
    REQUIRED_COLUMNS as STORYGRAPH_COLUMNS,
)
from ethos_api.schema import Category


@dataclass(frozen=True)
class ImportSignature:
    """Identidad de un export soportado y las cabeceras que lo delatan."""

    provider: str
    category: Category
    required_headers: frozenset[str] = field(default_factory=frozenset)


# Firmas CSV, en orden de prueba: la más específica primero (los tres CSV de
# Letterboxd comparten cabeceras base, así que diary → ratings → watched).
SIGNATURES: tuple[ImportSignature, ...] = (
    ImportSignature("goodreads", Category.books, GOODREADS_COLUMNS),
    ImportSignature("storygraph", Category.books, STORYGRAPH_COLUMNS),
    ImportSignature("applemusic", Category.music, APPLEMUSIC_COLUMNS),
    ImportSignature("imdb", Category.film, IMDB_COLUMNS),
    ImportSignature("letterboxd", Category.film, DIARY_COLUMNS),
    ImportSignature("letterboxd", Category.film, RATINGS_COLUMNS),
    ImportSignature("letterboxd", Category.film, WATCHED_COLUMNS),
)

_SPOTIFY = ImportSignature("spotify", Category.music)


def detect_import(text: str) -> ImportSignature | None:
    """Devuelve la firma del proveedor cuyo export coincide, o None."""
    stripped = text.lstrip()
    if stripped.startswith("["):
        # Spotify exporta JSON (historial simple o ampliado).
        try:
            records = json.loads(text)
        except json.JSONDecodeError:
            return None
        if isinstance(records, list) and looks_like_spotify(records):
            return _SPOTIFY
        return None
    reader = csv.reader(io.StringIO(text))
    try:
        headers = set(next(reader))
    except (StopIteration, csv.Error):
        return None
    for signature in SIGNATURES:
        if signature.required_headers <= headers:
            return signature
    return None
