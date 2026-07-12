"""Endpoints del slice de Libros: imports (Goodreads, StoryGraph) y APIs
(Open Library, Hardcover), estado y contexto."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ethos_api.auth import CurrentUserId
from ethos_api.books.context import build_books_context
from ethos_api.books.deps import BooksStoreDep, HardcoverClientDep, OpenLibraryClientDep
from ethos_api.books.service import (
    import_goodreads_csv,
    import_storygraph_csv,
    refresh_user_books_hardcover,
    refresh_user_books_openlibrary,
)
from ethos_api.books.summary import BooksSummary, build_books_summary
from ethos_api.connectors.goodreads.connector import GoodreadsImportError
from ethos_api.connectors.storygraph.connector import StorygraphImportError
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.schema import Category
from ethos_api.security import CipherDep
from ethos_api.sources_status import SyncState
from ethos_api.sources_support import replace_category_credential

router = APIRouter(tags=["books"])


class ConnectUsernameInput(BaseModel):
    """Username público con el que se lee el reading log (D62)."""

    user_name: str = Field(min_length=1, max_length=64)


class ConnectTokenInput(BaseModel):
    """Token de API del usuario (Hardcover, D62); se guarda cifrado (D20)."""

    token: str = Field(min_length=8, max_length=2048)


class BooksSourceOut(BaseModel):
    """Estado de la fuente de Libros para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    provider: str | None
    mode: str | None
    summary: BooksSummary | None


def _secret_for(
    user_id: str, provider: str, repo: RepositoryDep, cipher: CipherDep
) -> str:
    credential = repo.get(user_id, provider)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La fuente no está conectada; conéctala primero",
        )
    return cipher.decrypt(credential.encrypted_token)


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


@router.post("/sources/storygraph/import", status_code=status.HTTP_201_CREATED)
async def import_storygraph(
    request: Request,
    user_id: CurrentUserId,
    store: BooksStoreDep,
) -> dict[str, object]:
    """Importa el export CSV de StoryGraph y reemplaza los libros (D62)."""
    csv_text = await _csv_from(request)
    try:
        imported = import_storygraph_csv(user_id, csv_text, store)
    except StorygraphImportError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    return {"provider": "storygraph", "status": "imported", "items": imported}


@router.post("/sources/openlibrary", status_code=status.HTTP_201_CREATED)
def connect_openlibrary(
    body: ConnectUsernameInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: BooksStoreDep,
    client: OpenLibraryClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta Open Library por username y encola el primer refresco (D62)."""
    user_name = body.user_name.strip()
    replace_category_credential(
        repo, cipher, user_id, "openlibrary", Category.books, user_name
    )
    background.add_task(
        refresh_user_books_openlibrary, user_id, user_name, client, store
    )
    return {"provider": "openlibrary", "status": "connected"}


@router.post("/sources/openlibrary/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_openlibrary(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: BooksStoreDep,
    client: OpenLibraryClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo del reading log de Open Library (D62)."""
    user_name = _secret_for(user_id, "openlibrary", repo, cipher)
    background.add_task(
        refresh_user_books_openlibrary, user_id, user_name, client, store
    )
    return {"status": "queued"}


@router.post("/sources/hardcover", status_code=status.HTTP_201_CREATED)
def connect_hardcover(
    body: ConnectTokenInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: BooksStoreDep,
    client: HardcoverClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta Hardcover con el token del usuario y encola el refresco (D62)."""
    token = body.token.strip()
    replace_category_credential(
        repo, cipher, user_id, "hardcover", Category.books, token
    )
    background.add_task(refresh_user_books_hardcover, user_id, token, client, store)
    return {"provider": "hardcover", "status": "connected"}


@router.post("/sources/hardcover/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_hardcover(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: BooksStoreDep,
    client: HardcoverClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo de la biblioteca de Hardcover (D62)."""
    token = _secret_for(user_id, "hardcover", repo, cipher)
    background.add_task(refresh_user_books_hardcover, user_id, token, client, store)
    return {"status": "queued"}


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
        provider=source.provider,
        mode=source.mode,
        summary=summary,
    )


@router.get("/context/books")
def download_books_context(user_id: CurrentUserId, store: BooksStoreDep) -> JSONResponse:
    """Descarga `books.context.json` (D24) con el resumen de Libros (D48)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta una fuente de libros primero",
        )
    items = store.items_for_user(user_id)
    summary = build_books_summary(items, synced_at=source.synced_at)
    return JSONResponse(
        content=build_books_context(summary, items, provider=source.provider),
        headers={"Content-Disposition": 'attachment; filename="books.context.json"'},
    )
