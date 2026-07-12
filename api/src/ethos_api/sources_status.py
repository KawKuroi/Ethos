"""Estado de frescura de una fuente, compartido por todos los slices (D36).

Genérico: lo usan Juegos (con estado `private` para el perfil de Steam) y
Música. Incluye el mapeo con el enum `status` de la tabla `source_state`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class SyncState(StrEnum):
    """Estado de frescura de la fuente de un usuario."""

    never = "never"
    syncing = "syncing"
    fresh = "fresh"
    private = "private"
    error = "error"


@dataclass
class SourceStatus:
    """Estado del refresco de una fuente de un usuario.

    `provider` y `mode` identifican la fuente activa de la categoría (D4):
    con varios proveedores por categoría, la web y los contextos los leen de
    aquí en vez de asumir el proveedor inicial.
    """

    state: SyncState = SyncState.never
    synced_at: datetime | None = None
    detail: str | None = None
    provider: str | None = None
    mode: str | None = None


# Mapeo entre SyncState y el enum `status` de source_state (0001/0003).
STATE_TO_DB = {
    SyncState.never: "never_synced",
    SyncState.syncing: "syncing",
    SyncState.fresh: "synced",
    SyncState.private: "private",
    SyncState.error: "error",
}
DB_TO_STATE = {db: state for state, db in STATE_TO_DB.items()}
# `queued` (de la cola durable futura) se muestra como sincronizando.
DB_TO_STATE["queued"] = SyncState.syncing
