"""Endpoints para conectar, listar y desconectar credenciales de terceros."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from ethos_api.auth import CurrentUserId
from ethos_api.credentials.deps import RepositoryDep
from ethos_api.credentials.models import (
    ConnectCredentialInput,
    CredentialSummary,
    UserCredential,
)
from ethos_api.security import CipherDep

router = APIRouter(prefix="/credentials", tags=["credentials"])


def _to_summary(credential: UserCredential) -> CredentialSummary:
    return CredentialSummary(
        provider=credential.provider,
        category=credential.category,
        created_at=credential.created_at,
        updated_at=credential.updated_at,
    )


@router.post("", response_model=CredentialSummary, status_code=status.HTTP_201_CREATED)
def connect_credential(
    body: ConnectCredentialInput,
    user_id: CurrentUserId,
    repo: RepositoryDep,
    cipher: CipherDep,
) -> CredentialSummary:
    """Conecta (o actualiza) la credencial de un proveedor; la cifra al guardar."""
    now = datetime.now(UTC)
    existing = repo.get(user_id, body.provider)
    credential = UserCredential(
        user_id=user_id,
        provider=body.provider,
        category=body.category,
        encrypted_token=cipher.encrypt(body.token),
        created_at=existing.created_at if existing else now,
        updated_at=now,
    )
    repo.upsert(credential)
    return _to_summary(credential)


@router.get("", response_model=list[CredentialSummary])
def list_credentials(user_id: CurrentUserId, repo: RepositoryDep) -> list[CredentialSummary]:
    """Lista las credenciales del usuario, sin exponer los tokens."""
    return [_to_summary(c) for c in repo.list_for_user(user_id)]


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_credential(provider: str, user_id: CurrentUserId, repo: RepositoryDep) -> None:
    """Desconecta la credencial de un proveedor."""
    if not repo.delete(user_id, provider):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay credencial para ese proveedor",
        )
