"""Endpoints del slice de Cine y TV: conectar Trakt, refrescar y contexto."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ethos_api.auth import CurrentUserId
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.credentials.models import UserCredential
from ethos_api.film.context import build_film_context
from ethos_api.film.deps import FilmStoreDep, TraktClientDep
from ethos_api.film.service import refresh_user_film
from ethos_api.film.summary import FilmSummary, build_film_summary
from ethos_api.schema import Category
from ethos_api.security import CipherDep
from ethos_api.sources_status import SyncState

router = APIRouter(tags=["film"])

_PROVIDER = "trakt"


class ConnectTraktInput(BaseModel):
    """Username público de Trakt con el que se leen los datos vistos (D41)."""

    user_name: str = Field(min_length=1, max_length=64)


class FilmSourceOut(BaseModel):
    """Estado de la fuente de Cine y TV para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    summary: FilmSummary | None


def _user_name_for(user_id: str, repo: RepositoryDep, cipher: CipherDep) -> str:
    credential = repo.get(user_id, _PROVIDER)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trakt no está conectado; conecta la fuente primero",
        )
    return cipher.decrypt(credential.encrypted_token)


@router.post("/sources/trakt", status_code=status.HTTP_201_CREATED)
def connect_trakt(
    body: ConnectTraktInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: FilmStoreDep,
    client: TraktClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta la fuente por username y encola el primer refresco (D41)."""
    user_name = body.user_name.strip()
    now = datetime.now(UTC)
    existing = repo.get(user_id, _PROVIDER)
    repo.upsert(
        UserCredential(
            user_id=user_id,
            provider=_PROVIDER,
            category=Category.film,
            encrypted_token=cipher.encrypt(user_name),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
    )
    background.add_task(refresh_user_film, user_id, user_name, client, store)
    return {"provider": _PROVIDER, "status": "connected"}


@router.post("/sources/trakt/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_trakt(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: FilmStoreDep,
    client: TraktClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo de lo visto (D44)."""
    user_name = _user_name_for(user_id, repo, cipher)
    background.add_task(refresh_user_film, user_id, user_name, client, store)
    return {"status": "queued"}


@router.get("/sources/film", response_model=FilmSourceOut)
def film_status(user_id: CurrentUserId, store: FilmStoreDep) -> FilmSourceOut:
    """Estado de frescura de la fuente de Cine y TV y su resumen (si hay datos)."""
    source = store.status_for_user(user_id)
    items = store.items_for_user(user_id)
    stats = store.stats_for_user(user_id)
    summary = (
        build_film_summary(items, stats, synced_at=source.synced_at)
        if items or stats
        else None
    )
    return FilmSourceOut(
        state=source.state,
        synced_at=source.synced_at,
        detail=source.detail,
        summary=summary,
    )


@router.get("/context/film")
def download_film_context(user_id: CurrentUserId, store: FilmStoreDep) -> JSONResponse:
    """Descarga `film.context.json` (D24) con el resumen de Cine y TV (D43)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta Trakt y espera el refresco",
        )
    items = store.items_for_user(user_id)
    summary = build_film_summary(
        items,
        store.stats_for_user(user_id),
        synced_at=source.synced_at,
    )
    return JSONResponse(
        content=build_film_context(summary, items),
        headers={"Content-Disposition": 'attachment; filename="film.context.json"'},
    )
