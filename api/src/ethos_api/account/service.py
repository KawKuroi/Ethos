"""Lógica del borrado de datos y de cuenta diferido (D53).

Opera sobre PostgREST (service_role). El borrado de datos limpia el contexto
del usuario conservando la cuenta; el borrado de cuenta programa una purga a 30
días que un job vencido ejecuta (borra el usuario de auth.users, que cascada al
resto de tablas propias). El deshacer solo cancela la programación.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from ethos_api.account.models import DeletionStatus
from ethos_api.supabase_rest import SupabaseRest

# Tablas con datos de contexto del usuario que borra "eliminar todos los datos"
# (la cuenta, sus tokens del MCP y su feedback se conservan).
_DATA_TABLES = ("user_items", "user_events", "source_state", "user_credentials")

_TABLE = "account_deletions"
UNDO_DAYS = 30


def wipe_user_data(rest: SupabaseRest, user_id: str) -> None:
    """Borra el contexto del usuario (items, eventos, estado y credenciales)."""
    for table in _DATA_TABLES:
        rest.delete(table, {"user_id": f"eq.{user_id}"})


def schedule_deletion(
    rest: SupabaseRest, user_id: str, *, now: datetime | None = None
) -> DeletionStatus:
    """Programa el borrado de la cuenta a `UNDO_DAYS` días (idempotente)."""
    requested = now or datetime.now(UTC)
    purge_after = requested + timedelta(days=UNDO_DAYS)
    rest.upsert(
        _TABLE,
        [
            {
                "user_id": user_id,
                "requested_at": requested.isoformat(),
                "purge_after": purge_after.isoformat(),
            }
        ],
        on_conflict="user_id",
    )
    return DeletionStatus(requested_at=requested, purge_after=purge_after)


def deletion_status(rest: SupabaseRest, user_id: str) -> DeletionStatus | None:
    """Devuelve la programación de borrado del usuario, o None si no hay."""
    rows = rest.select(
        _TABLE,
        {"user_id": f"eq.{user_id}", "select": "requested_at,purge_after", "limit": "1"},
    )
    if not rows:
        return None
    row = rows[0]
    return DeletionStatus(
        requested_at=datetime.fromisoformat(row["requested_at"]),
        purge_after=datetime.fromisoformat(row["purge_after"]),
    )


def cancel_deletion(rest: SupabaseRest, user_id: str) -> bool:
    """Cancela (deshace) el borrado programado; True si había uno."""
    return rest.delete(_TABLE, {"user_id": f"eq.{user_id}"}) > 0


def purge_due_accounts(
    rest: SupabaseRest,
    delete_auth_user: Callable[[str], None],
    *,
    now: datetime | None = None,
) -> int:
    """Purga las cuentas vencidas: borra el usuario de auth (cascada) y su marca.

    Pensado para un job programado. Devuelve cuántas cuentas purgó.
    """
    moment = now or datetime.now(UTC)
    rows = rest.select(
        _TABLE, {"select": "user_id", "purge_after": f"lte.{moment.isoformat()}"}
    )
    purged = 0
    for row in rows:
        user_id = row["user_id"]
        delete_auth_user(user_id)
        rest.delete(_TABLE, {"user_id": f"eq.{user_id}"})
        purged += 1
    return purged
