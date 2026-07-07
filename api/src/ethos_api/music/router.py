"""Endpoints del slice de música: conectar ListenBrainz, refrescar y contexto."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ethos_api.auth import CurrentUserId
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.credentials.models import UserCredential
from ethos_api.music.context import build_music_context
from ethos_api.music.deps import EventStoreDep, ListenBrainzClientDep
from ethos_api.music.service import refresh_user_music
from ethos_api.music.summary import MusicSummary, build_music_summary
from ethos_api.schema import Category
from ethos_api.security import CipherDep
from ethos_api.sources_status import SyncState

router = APIRouter(tags=["music"])

_PROVIDER = "listenbrainz"


class ConnectListenBrainzInput(BaseModel):
    """Username público de ListenBrainz con el que se leen los listens (D37)."""

    user_name: str = Field(min_length=1, max_length=64)


class MusicSourceOut(BaseModel):
    """Estado de la fuente de música para la web, con el resumen si lo hay."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    summary: MusicSummary | None


def _user_name_for(user_id: str, repo: RepositoryDep, cipher: CipherDep) -> str:
    credential = repo.get(user_id, _PROVIDER)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ListenBrainz no está conectado; conecta la fuente primero",
        )
    return cipher.decrypt(credential.encrypted_token)


@router.post("/sources/listenbrainz", status_code=status.HTTP_201_CREATED)
def connect_listenbrainz(
    body: ConnectListenBrainzInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: EventStoreDep,
    client: ListenBrainzClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Conecta la fuente por username y encola el primer refresco (D37)."""
    user_name = body.user_name.strip()
    now = datetime.now(UTC)
    existing = repo.get(user_id, _PROVIDER)
    repo.upsert(
        UserCredential(
            user_id=user_id,
            provider=_PROVIDER,
            category=Category.music,
            encrypted_token=cipher.encrypt(user_name),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
    )
    background.add_task(refresh_user_music, user_id, user_name, client, store)
    return {"provider": _PROVIDER, "status": "connected"}


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
    user_name = _user_name_for(user_id, repo, cipher)
    background.add_task(refresh_user_music, user_id, user_name, client, store)
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
        summary=summary,
    )


@router.get("/context/music")
def download_music_context(user_id: CurrentUserId, store: EventStoreDep) -> JSONResponse:
    """Descarga `music.context.json` (D24) con el resumen temporal (D39)."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta ListenBrainz y espera el refresco",
        )
    events = store.events_for_user(user_id)
    summary = build_music_summary(events)
    return JSONResponse(
        content=build_music_context(summary, events),
        headers={"Content-Disposition": 'attachment; filename="music.context.json"'},
    )
