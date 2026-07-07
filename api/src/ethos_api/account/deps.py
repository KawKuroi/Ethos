"""Dependencia del cliente PostgREST para las operaciones de cuenta.

Las operaciones de cuenta (borrado de datos y programación de purga) requieren
Supabase: sin él (local/CI sin backend) devuelven 503. Los tests lo sustituyen
con un PostgREST simulado vía `dependency_overrides`.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from ethos_api.supabase_rest import SupabaseRest, get_rest


def get_account_rest() -> SupabaseRest:
    rest = get_rest()
    if rest is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El borrado de cuenta requiere el backend de datos configurado",
        )
    return rest


AccountRestDep = Annotated[SupabaseRest, Depends(get_account_rest)]
