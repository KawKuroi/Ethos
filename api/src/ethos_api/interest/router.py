"""Endpoint para registrar interés en categorías en desarrollo (D50).

Público: lo usa tanto un visitante de la landing (solo correo) como un usuario
con sesión (se asocia su `user_id` si el JWT es válido). Idempotente por
(correo, categoría); protegido por el rate limit por IP de la app.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from ethos_api.auth import OptionalUserId
from ethos_api.interest.deps import RepositoryDep
from ethos_api.interest.models import (
    DEFERRED_CATEGORIES,
    CategoryInterest,
    CategoryInterestInput,
)

router = APIRouter(prefix="/category-interest", tags=["interest"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def register_interest(
    body: CategoryInterestInput,
    user_id: OptionalUserId,
    repo: RepositoryDep,
) -> None:
    """Registra el interés en avisar cuando una categoría diferida se active."""
    if body.category not in DEFERRED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Esa categoría no está en desarrollo",
        )
    repo.add(
        CategoryInterest(
            email=str(body.email),
            category=body.category,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
    )
