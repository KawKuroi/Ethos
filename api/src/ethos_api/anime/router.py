"""Endpoints del slice de Anime y manga: conectar AniList, MyAnimeList o Kitsu."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ethos_api.anime.context import build_anime_context
from ethos_api.anime.deps import (
    AniListClientDep,
    AnimeStoreDep,
    KitsuClientDep,
    MalClientDep,
)
from ethos_api.anime.service import (
    refresh_user_anime,
    refresh_user_anime_kitsu,
    refresh_user_anime_mal,
)
from ethos_api.anime.summary import AnimeSummary, build_anime_summary
from ethos_api.auth import CurrentUserId
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.schema import Category
from ethos_api.security import CipherDep
from ethos_api.sources_status import SyncState
from ethos_api.sources_support import replace_category_credential

router = APIRouter(tags=["anime"])


class ConnectUsernameInput(BaseModel):
    """Username público con el que se leen las listas (D45/D62)."""

    user_name: str = Field(min_length=1, max_length=64)


class AnimeSourceOut(BaseModel):
    """Estado de la fuente de Anime y manga para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    provider: str | None
    mode: str | None
    summary: AnimeSummary | None


def _user_name_for(
    user_id: str, provider: str, repo: RepositoryDep, cipher: CipherDep
) -> str:
    credential = repo.get(user_id, provider)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La fuente no está conectada; conéctala primero",
        )
    return cipher.decrypt(credential.encrypted_token)


@router.post("/sources/anilist", status_code=status.HTTP_201_CREATED)
def connect_anilist(
    body: ConnectUsernameInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: AniListClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta AniList por username y encola el primer refresco (D45)."""
    user_name = body.user_name.strip()
    replace_category_credential(
        repo, cipher, user_id, "anilist", Category.anime, user_name
    )
    background.add_task(refresh_user_anime, user_id, user_name, client, store)
    return {"provider": "anilist", "status": "connected"}


@router.post("/sources/anilist/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_anilist(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: AniListClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo de las listas de AniList (D46)."""
    user_name = _user_name_for(user_id, "anilist", repo, cipher)
    background.add_task(refresh_user_anime, user_id, user_name, client, store)
    return {"status": "queued"}


@router.post("/sources/mal", status_code=status.HTTP_201_CREATED)
def connect_mal(
    body: ConnectUsernameInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: MalClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta MyAnimeList por username y encola el primer refresco (D62)."""
    user_name = body.user_name.strip()
    replace_category_credential(repo, cipher, user_id, "mal", Category.anime, user_name)
    background.add_task(refresh_user_anime_mal, user_id, user_name, client, store)
    return {"provider": "mal", "status": "connected"}


@router.post("/sources/mal/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_mal(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: MalClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo de las listas de MyAnimeList (D62)."""
    user_name = _user_name_for(user_id, "mal", repo, cipher)
    background.add_task(refresh_user_anime_mal, user_id, user_name, client, store)
    return {"status": "queued"}


@router.post("/sources/kitsu", status_code=status.HTTP_201_CREATED)
def connect_kitsu(
    body: ConnectUsernameInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: KitsuClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta Kitsu por username y encola el primer refresco (D62)."""
    user_name = body.user_name.strip()
    replace_category_credential(
        repo, cipher, user_id, "kitsu", Category.anime, user_name
    )
    background.add_task(refresh_user_anime_kitsu, user_id, user_name, client, store)
    return {"provider": "kitsu", "status": "connected"}


@router.post("/sources/kitsu/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_kitsu(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: AnimeStoreDep,
    client: KitsuClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco completo de la biblioteca de Kitsu (D62)."""
    user_name = _user_name_for(user_id, "kitsu", repo, cipher)
    background.add_task(refresh_user_anime_kitsu, user_id, user_name, client, store)
    return {"status": "queued"}


@router.get("/sources/anime", response_model=AnimeSourceOut)
def anime_status(user_id: CurrentUserId, store: AnimeStoreDep) -> AnimeSourceOut:
    """Estado de frescura de la fuente de Anime y manga y su resumen."""
    source = store.status_for_user(user_id)
    items = store.items_for_user(user_id)
    summary = build_anime_summary(items, synced_at=source.synced_at) if items else None
    return AnimeSourceOut(
        state=source.state,
        synced_at=source.synced_at,
        detail=source.detail,
        provider=source.provider,
        mode=source.mode,
        summary=summary,
    )


@router.get("/context/anime")
def download_anime_context(user_id: CurrentUserId, store: AnimeStoreDep) -> JSONResponse:
    """Descarga `anime.context.json` (D24) con el resumen de Anime y manga (D46)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta una fuente y espera el refresco",
        )
    items = store.items_for_user(user_id)
    summary = build_anime_summary(items, synced_at=source.synced_at)
    return JSONResponse(
        content=build_anime_context(summary, items, provider=source.provider),
        headers={"Content-Disposition": 'attachment; filename="anime.context.json"'},
    )
