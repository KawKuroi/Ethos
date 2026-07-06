"""Modelos de la lista de interés en categorías en desarrollo (D50)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr

# Categorías diferidas fuera del catálogo activo (D27/D31); ids del diseño.
# Son las únicas para las que tiene sentido registrar interés: las activas ya
# se pueden conectar.
DEFERRED_CATEGORIES: frozenset[str] = frozenset({"places", "food", "board"})


class CategoryInterestInput(BaseModel):
    """Entrada para registrar interés en una categoría en desarrollo."""

    category: str
    email: EmailStr


class CategoryInterest(BaseModel):
    """Registro de interés almacenado."""

    email: str
    category: str
    user_id: str | None = None
    created_at: datetime
