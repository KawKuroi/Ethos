"""Modelos del borrado de cuenta diferido (D53)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DeletionStatus(BaseModel):
    """Estado de un borrado de cuenta programado."""

    requested_at: datetime
    purge_after: datetime


class DeletionStatusOut(BaseModel):
    """Respuesta del estado de borrado: `scheduled` False si no hay ninguno."""

    scheduled: bool
    purge_after: datetime | None = None
