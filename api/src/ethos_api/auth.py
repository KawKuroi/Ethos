"""Autenticación de sesión: verifica el JWT de Supabase Auth.

La dependencia `get_current_user_id` extrae y valida el Bearer token (HS256 con
el secreto del proyecto) y devuelve el id del usuario (`sub`). No hace red.
"""

from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ethos_api.config import settings

_bearer = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    """Valida el JWT de sesión y devuelve el id del usuario autenticado."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de sesión",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sesión inválido",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sesión sin sujeto",
        )
    return str(user_id)


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
