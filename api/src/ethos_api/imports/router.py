"""Endpoint del import genérico: autodetecta el proveedor y delega (D49)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from ethos_api.auth import CurrentUserId
from ethos_api.books.deps import BooksStoreDep
from ethos_api.books.service import import_goodreads_csv
from ethos_api.connectors.goodreads.connector import GoodreadsImportError
from ethos_api.imports.detection import detect_import

router = APIRouter(tags=["imports"])

_UNRECOGNIZED = (
    "No reconocimos el archivo. Sube el export original de tu proveedor "
    "(hoy soportamos el CSV de Goodreads: My Books → Import and export → "
    "Export Library)."
)


@router.post("/imports", status_code=status.HTTP_201_CREATED)
async def generic_import(
    request: Request,
    user_id: CurrentUserId,
    books_store: BooksStoreDep,
) -> dict[str, object]:
    """Detecta el proveedor por la firma del archivo y ejecuta su import."""
    body = await request.body()
    text = body.decode("utf-8-sig", errors="replace")
    signature = detect_import(text)
    if signature is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=_UNRECOGNIZED
        )
    # v1: Goodreads es el único flujo de import; los siguientes se despachan
    # aquí por proveedor detectado.
    try:
        imported = import_goodreads_csv(user_id, text, books_store)
    except GoodreadsImportError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    return {
        "provider": signature.provider,
        "category": signature.category.value,
        "status": "imported",
        "items": imported,
    }
