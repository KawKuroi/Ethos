"""Endpoints del slice de Libros: import de Goodreads, estado y contexto."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ethos_api.auth import CurrentUserId
from ethos_api.books.context import build_books_context
from ethos_api.books.deps import BooksStoreDep
from ethos_api.books.service import import_goodreads_csv
from ethos_api.books.summary import BooksSummary, build_books_summary
from ethos_api.connectors.goodreads.connector import GoodreadsImportError
from ethos_api.sources_status import SyncState

router = APIRouter(tags=["books"])


class BooksSourceOut(BaseModel):
    """Estado de la fuente de Libros para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    summary: BooksSummary | None


async def _csv_from(request: Request) -> str:
    # El export viaja como texto plano (text/csv); utf-8-sig tolera el BOM
    # con que Goodreads genera el archivo.
    body = await request.body()
    return body.decode("utf-8-sig", errors="replace")


@router.post("/sources/goodreads/import", status_code=status.HTTP_201_CREATED)
async def import_goodreads(
    request: Request,
    user_id: CurrentUserId,
    store: BooksStoreDep,
) -> dict[str, object]:
    """Importa el export CSV de Goodreads y reemplaza los libros (D47)."""
    csv_text = await _csv_from(request)
    try:
        imported = import_goodreads_csv(user_id, csv_text, store)
    except GoodreadsImportError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    return {"provider": "goodreads", "status": "imported", "items": imported}


@router.get("/sources/books", response_model=BooksSourceOut)
def books_status(user_id: CurrentUserId, store: BooksStoreDep) -> BooksSourceOut:
    """Estado de frescura de la fuente de Libros y su resumen (si hay datos)."""
    source = store.status_for_user(user_id)
    items = store.items_for_user(user_id)
    summary = (
        build_books_summary(items, synced_at=source.synced_at) if items else None
    )
    return BooksSourceOut(
        state=source.state,
        synced_at=source.synced_at,
        detail=source.detail,
        summary=summary,
    )


@router.get("/context/books")
def download_books_context(user_id: CurrentUserId, store: BooksStoreDep) -> JSONResponse:
    """Descarga `books.context.json` (D24) con el resumen de Libros (D48)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: sube tu export de Goodreads primero",
        )
    summary = build_books_summary(
        store.items_for_user(user_id), synced_at=source.synced_at
    )
    return JSONResponse(
        content=build_books_context(summary),
        headers={"Content-Disposition": 'attachment; filename="books.context.json"'},
    )
