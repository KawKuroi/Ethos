"""Autenticación de sesión: verifica el JWT de Supabase Auth.

La dependencia `get_current_user_id` extrae y valida el Bearer token y devuelve
el id del usuario (`sub`). Soporta los dos esquemas de firma de Supabase:

- Llaves de firma asimétricas (ES256/RS256), el esquema de los proyectos
  nuevos: se verifican contra el endpoint JWKS del proyecto, con caché de
  llaves. El backend solo maneja llaves públicas.
- Secreto compartido legacy (HS256): se usa cuando el token lo declara y
  `SUPABASE_JWT_SECRET` está configurado.

En ambos casos se exige `exp` y `sub`, se valida `aud="authenticated"` y,
si hay `SUPABASE_URL`, también el emisor (`iss`).
"""

from __future__ import annotations

from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ethos_api.config import settings

_bearer = HTTPBearer(auto_error=False)

_ASYMMETRIC_ALGORITHMS = ["ES256", "RS256"]

# Clientes JWKS por URL, con caché de llaves (PyJWKClient cachea el set y las
# llaves de firma). Se crean perezosamente porque la URL llega por entorno.
_jwks_clients: dict[str, jwt.PyJWKClient] = {}


def _jwks_client(supabase_url: str) -> jwt.PyJWKClient:
    url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    client = _jwks_clients.get(url)
    if client is None:
        client = jwt.PyJWKClient(url, cache_keys=True)
        _jwks_clients[url] = client
    return client


def _decode(token: str) -> dict[str, Any]:
    """Verifica firma y claims del token; lanza `jwt.PyJWTError` si falla."""
    algorithm = str(jwt.get_unverified_header(token).get("alg", ""))
    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1" if settings.supabase_url else None
    common: dict[str, Any] = {
        "audience": "authenticated",
        "issuer": issuer,
        "options": {"require": ["exp", "sub"]},
    }

    if algorithm in _ASYMMETRIC_ALGORITHMS:
        if not settings.supabase_url:
            raise jwt.InvalidTokenError("Sin SUPABASE_URL para verificar contra JWKS")
        signing_key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token)
        return jwt.decode(token, signing_key.key, algorithms=_ASYMMETRIC_ALGORITHMS, **common)

    secret = settings.supabase_jwt_secret.get_secret_value()
    if not secret:
        raise jwt.InvalidTokenError("Sin SUPABASE_JWT_SECRET para verificar HS256")
    return jwt.decode(token, secret, algorithms=["HS256"], **common)


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
        payload = _decode(credentials.credentials)
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


def get_optional_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str | None:
    """Devuelve el id del usuario si hay un JWT válido; None si no hay o falla.

    Para endpoints usables tanto por un visitante anónimo (landing pública)
    como por un usuario con sesión (panel), sin exigir autenticación.
    """
    if credentials is None:
        return None
    try:
        payload = _decode(credentials.credentials)
    except jwt.PyJWTError:
        return None
    user_id = payload.get("sub")
    return str(user_id) if user_id else None


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
OptionalUserId = Annotated[str | None, Depends(get_optional_user_id)]
