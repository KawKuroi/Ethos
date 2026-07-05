"""Endpoints del slice de Anime y manga: conectar AniList, refrescar y contexto."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ethos_api.anime.context import build_anime_context
from ethos_api.anime.deps import AniListClientDep, AnimeStoreDep
from ethos_api.anime.service import refresh_user_anime
from ethos_api.anime.summary import AnimeSummary, build_anime_summary
from ethos_api.auth import CurrentUserId
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.credentials.models import UserCredential
from ethos_api.schema import Category
from ethos_api.security import CipherDep
from ethos_api.sources_status import SyncState

router = APIRouter(tags=["anime"])

_PROVIDER = "anilist"


class ConnectAniListInput(BaseModel):
    """Username público de AniList con el que se leen las listas (D45)."""

    user_name: str = Field(min_length=1, max_length=64)


class AnimeSourceOut(BaseModel):
    """Estado de la fuente de Anime y manga para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    summary: AnimeSummary | None


def _user_name_for(user_id: str, repo: RepositoryDep, cipher: CipherDep) -> str:
    credential = repo.get(user_id, _PROVIDER)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AniList no está conectado; conecta la fuente primero",
        )
    return cipher.decrypt(credential.encrypted_token)


@router.post("/sources/anilist", status_code=status.HTTP_201_CREATED)
def connect_anilist(
    body: ConnectAniListInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: AniListClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta la fuente por username y encola el primer refresco (D45)."""
    user_name = body.user_name.strip()
    now = datetime.now(UTC)
    existing = repo.get(user_id, _PROVIDER)
    repo.upsert(
        UserCredential(
            user_id=user_id,
            provider=_PROVIDER,
            category=Category.anime,
            encrypted_token=cipher.encrypt(user_name),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
    )
    background.add_task(refresh_user_anime, user_id, user_name, client, store)
    return {"provider": _PROVIDER, "status": "connected"}


@router.post("/sources/anilist/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_anilist(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: AniListClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo de las listas (D45)."""
    user_name = _user_name_for(user_id, repo, cipher)
    background.add_task(refresh_user_anime, user_id, user_name, client, store)
    return {"status": "queued"}


@router.get("/sources/anime", response_model=AnimeSourceOut)
def anime_status(user_id: CurrentUserId, store: AnimeStoreDep) -> AnimeSourceOut:
    """Estado de frescura de la fuente de Anime y manga y su resumen (si hay datos)."""
    source = store.status_for_user(user_id)
    items = store.items_for_user(user_id)
    summary = (
        build_anime_summary(items, synced_at=source.synced_at) if items else None
    )
    return AnimeSourceOut(
        state=source.state,
        synced_at=source.synced_at,
        detail=source.detail,
        summary=summary,
    )


@router.get("/context/anime")
def download_anime_context(user_id: CurrentUserId, store: AnimeStoreDep) -> JSONResponse:
    """Descarga `anime.context.json` (D24) con el resumen de Anime y manga (D46)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta AniList y espera el refresco",
        )
    summary = build_anime_summary(
        store.items_for_user(user_id), synced_at=source.synced_at
    )
    return JSONResponse(
        content=build_anime_context(summary),
        headers={"Content-Disposition": 'attachment; filename="anime.context.json"'},
    )
