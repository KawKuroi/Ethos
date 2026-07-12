"""Endpoints del slice de música: conectar ListenBrainz o Last.fm, refrescar y contexto."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ethos_api.auth import CurrentUserId
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.music.context import build_music_context
from ethos_api.music.deps import EventStoreDep, LastfmClientDep, ListenBrainzClientDep
from ethos_api.music.service import refresh_user_music, refresh_user_music_lastfm
from ethos_api.music.summary import MusicSummary, build_music_summary
from ethos_api.schema import Category
from ethos_api.security import CipherDep
from ethos_api.sources_status import SyncState
from ethos_api.sources_support import replace_category_credential

router = APIRouter(tags=["music"])


class ConnectUsernameInput(BaseModel):
    """Username público con el que se leen los listens (D37/D62)."""

    user_name: str = Field(min_length=1, max_length=64)


class MusicSourceOut(BaseModel):
    """Estado de la fuente de música para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    provider: str | None
    mode: str | None
    summary: MusicSummary | None


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


@router.post("/sources/listenbrainz", status_code=status.HTTP_201_CREATED)
def connect_listenbrainz(
    body: ConnectUsernameInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: EventStoreDep,
    client: ListenBrainzClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta la fuente por username y encola el primer refresco (D37)."""
    user_name = body.user_name.strip()
    replace_category_credential(
        repo, cipher, user_id, "listenbrainz", Category.music, user_name
    )
    background.add_task(
        refresh_user_music, user_id, user_name, client, store, replace=True
    )
    return {"provider": "listenbrainz", "status": "connected"}


@router.post("/sources/listenbrainz/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_listenbrainz(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: EventStoreDep,
    client: ListenBrainzClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco incremental de los listens (D40)."""
    user_name = _user_name_for(user_id, "listenbrainz", repo, cipher)
    background.add_task(refresh_user_music, user_id, user_name, client, store)
    return {"status": "queued"}


@router.post("/sources/lastfm", status_code=status.HTTP_201_CREATED)
def connect_lastfm(
    body: ConnectUsernameInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: EventStoreDep,
    client: LastfmClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta Last.fm por username y encola el primer refresco (D62)."""
    user_name = body.user_name.strip()
    replace_category_credential(
        repo, cipher, user_id, "lastfm", Category.music, user_name
    )
    background.add_task(
        refresh_user_music_lastfm, user_id, user_name, client, store, replace=True
    )
    return {"provider": "lastfm", "status": "connected"}


@router.post("/sources/lastfm/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_lastfm(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: EventStoreDep,
    client: LastfmClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco incremental de los scrobbles de Last.fm (D62)."""
    user_name = _user_name_for(user_id, "lastfm", repo, cipher)
    background.add_task(refresh_user_music_lastfm, user_id, user_name, client, store)
    return {"status": "queued"}


@router.get("/sources/music", response_model=MusicSourceOut)
def music_status(user_id: CurrentUserId, store: EventStoreDep) -> MusicSourceOut:
    """Estado de frescura de la fuente de música y su resumen (si hay datos)."""
    source = store.status_for_user(user_id)
    events = store.events_for_user(user_id)
    summary = build_music_summary(events) if events else None
    return MusicSourceOut(
        state=source.state,
        synced_at=source.synced_at,
        detail=source.detail,
        provider=source.provider,
        mode=source.mode,
        summary=summary,
    )


@router.get("/context/music")
def download_music_context(user_id: CurrentUserId, store: EventStoreDep) -> JSONResponse:
    """Descarga `music.context.json` (D24) con el resumen temporal (D39)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta una fuente y espera el refresco",
        )
    events = store.events_for_user(user_id)
    summary = build_music_summary(events)
    return JSONResponse(
        content=build_music_context(summary, events, provider=source.provider),
        headers={"Content-Disposition": 'attachment; filename="music.context.json"'},
    )
