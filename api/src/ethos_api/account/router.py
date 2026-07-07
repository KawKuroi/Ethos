"""Endpoints de borrado de datos y de cuenta (D53).

Todos autenticados y acotados al propio usuario. "Eliminar datos" limpia el
contexto conservando la cuenta; "Eliminar cuenta" programa una purga a 30 días
con deshacer. La purga real la ejecuta un job programado (ver account/service).
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, status

from ethos_api.account.deps import AccountRestDep
from ethos_api.account.mailer import notify_deletion_scheduled
from ethos_api.account.models import DeletionStatusOut
from ethos_api.account.service import (
    cancel_deletion,
    deletion_status,
    schedule_deletion,
    wipe_user_data,
)
from ethos_api.auth import CurrentUserEmail, CurrentUserId

router = APIRouter(prefix="/account", tags=["account"])


@router.delete("/data", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_data(user_id: CurrentUserId, rest: AccountRestDep) -> None:
    """Borra el contexto del usuario (items, eventos, estado, credenciales)."""
    wipe_user_data(rest, user_id)


@router.post("/deletion", response_model=DeletionStatusOut)
def request_account_deletion(
    user_id: CurrentUserId,
    email: CurrentUserEmail,
    rest: AccountRestDep,
    background: BackgroundTasks,
) -> DeletionStatusOut:
    """Programa el borrado de la cuenta a 30 días y avisa por correo."""
    status_ = schedule_deletion(rest, user_id)
    background.add_task(notify_deletion_scheduled, email, status_.purge_after)
    return DeletionStatusOut(scheduled=True, purge_after=status_.purge_after)


@router.get("/deletion", response_model=DeletionStatusOut)
def get_account_deletion(user_id: CurrentUserId, rest: AccountRestDep) -> DeletionStatusOut:
    """Estado del borrado programado del usuario (si lo hay)."""
    status_ = deletion_status(rest, user_id)
    if status_ is None:
        return DeletionStatusOut(scheduled=False)
    return DeletionStatusOut(scheduled=True, purge_after=status_.purge_after)


@router.delete("/deletion", status_code=status.HTTP_204_NO_CONTENT)
def undo_account_deletion(user_id: CurrentUserId, rest: AccountRestDep) -> None:
    """Deshace (cancela) el borrado programado de la cuenta."""
    cancel_deletion(rest, user_id)
