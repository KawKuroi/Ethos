"""Endpoints del slice de juegos: conectar Steam, refrescar y contexto."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ethos_api.auth import CurrentUserId
from ethos_api.connectors.steam.openid import SteamOpenIdError
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.credentials.models import UserCredential
from ethos_api.games.context import build_games_context
from ethos_api.games.deps import GamesStoreDep, OpenIdVerifierDep, SteamClientDep
from ethos_api.games.service import refresh_user_games
from ethos_api.games.store import SyncState
from ethos_api.games.summary import build_games_summary
from ethos_api.schema import Category, ItemStatus
from ethos_api.security import CipherDep

router = APIRouter(tags=["games"])

_STEAM_PROVIDER = "steam"


class SteamOpenIdInput(BaseModel):
    """Parámetros `openid.*` con los que Steam volvió a la web."""

    params: dict[str, str]


class SourceStatusOut(BaseModel):
    """Estado de la fuente de juegos para la web."""

    state: SyncState
    synced_at: datetime | None
    detail: str | None
    games: int
    wishlisted: int
    persona_name: str | None


def _steamid_for(user_id: str, repo: RepositoryDep, cipher: CipherDep) -> str:
    credential = repo.get(user_id, _STEAM_PROVIDER)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Steam no está conectado; conecta la fuente primero",
        )
    return cipher.decrypt(credential.encrypted_token)


@router.post("/sources/steam", status_code=status.HTTP_201_CREATED)
def connect_steam(
    body: SteamOpenIdInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: GamesStoreDep,
    client: SteamClientDep,
    verifier: OpenIdVerifierDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Verifica el retorno OpenID de Steam y conecta la fuente (D12).

    El steamid se guarda cifrado como credencial del proveedor y se encola el
    primer refresco.
    """
    try:
        steamid = verifier(body.params)
    except SteamOpenIdError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error

    now = datetime.now(UTC)
    existing = repo.get(user_id, _STEAM_PROVIDER)
    repo.upsert(
        UserCredential(
            user_id=user_id,
            provider=_STEAM_PROVIDER,
            category=Category.games,
            encrypted_token=cipher.encrypt(steamid),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
    )
    background.add_task(refresh_user_games, user_id, steamid, client, store)
    return {"provider": _STEAM_PROVIDER, "status": "connected"}


@router.post("/sources/steam/refresh", status_code=status.HTTP_202_ACCEPTED)
def refresh_steam(
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
    store: GamesStoreDep,
    client: SteamClientDep,
    background: BackgroundTasks,
) -> dict[str, str]:
    """Encola un refresco de la biblioteca (asíncrono, D36)."""
    steamid = _steamid_for(user_id, repo, cipher)
    background.add_task(refresh_user_games, user_id, steamid, client, store)
    return {"status": "queued"}


@router.get("/sources/games", response_model=SourceStatusOut)
def games_status(user_id: CurrentUserId, store: GamesStoreDep) -> SourceStatusOut:
    """Estado de frescura y conteos de la fuente de juegos."""
    source = store.status_for_user(user_id)
    items = store.items_for_user(user_id)
    profile = store.profile_for_user(user_id)
    return SourceStatusOut(
        state=source.state,
        synced_at=source.synced_at,
        detail=source.detail,
        games=sum(1 for i in items if i.status is ItemStatus.in_library),
        wishlisted=sum(1 for i in items if i.status is ItemStatus.wishlist),
        persona_name=profile.persona_name if profile else None,
    )


@router.get("/context/games")
def download_games_context(user_id: CurrentUserId, store: GamesStoreDep) -> JSONResponse:
    """Descarga `games.context.json` (D24) con la forma fijada en D34."""
    source = store.status_for_user(user_id)
    if source.state in (SyncState.never, SyncState.syncing):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay contexto: conecta Steam y espera el primer refresco",
        )
    items = store.items_for_user(user_id)
    profile = store.profile_for_user(user_id)
    summary = build_games_summary(items, profile, synced_at=source.synced_at)
    context = build_games_context(summary, items, profile)
    return JSONResponse(
        content=context,
        headers={"Content-Disposition": 'attachment; filename="games.context.json"'},
    )
