"""Autodetección del proveedor de un archivo de import (D49).

Cada proveedor de import declara una firma: las cabeceras que identifican su
export. La detección lee la primera fila del CSV y busca la primera firma cuyo
conjunto de cabeceras esté contenido en el archivo. Añadir un proveedor de
import es registrar aquí su firma y su flujo.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from ethos_api.connectors.goodreads.connector import REQUIRED_COLUMNS
from ethos_api.schema import Category


@dataclass(frozen=True)
class ImportSignature:
    """Identidad de un export soportado y las cabeceras que lo delatan."""

    provider: str
    category: Category
    required_headers: frozenset[str]


# Firmas soportadas, en orden de prueba (v1: solo Goodreads).
SIGNATURES: tuple[ImportSignature, ...] = (
    ImportSignature(
        provider="goodreads",
        category=Category.books,
        required_headers=REQUIRED_COLUMNS,
    ),
)


def detect_import(text: str) -> ImportSignature | None:
    """Devuelve la firma del proveedor cuyo export coincide, o None."""
    reader = csv.reader(io.StringIO(text))
    try:
        headers = set(next(reader))
    except (StopIteration, csv.Error):
        return None
    for signature in SIGNATURES:
        if signature.required_headers <= headers:
            return signature
    return None
