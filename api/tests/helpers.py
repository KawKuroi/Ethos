"""Helpers compartidos de la suite: emisión de JWT de prueba."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

# Secreto legacy HS256 de prueba (>=32 bytes para evitar el aviso de PyJWT).
JWT_SECRET = "clave-de-prueba-para-jwt-de-al-menos-32-bytes"


def make_token(user: str = "user-1", *, secret: str = JWT_SECRET, **overrides: object) -> str:
    """Emite un JWT de sesión de prueba (HS256).

    Los claims por defecto son válidos; `overrides` los sustituye y un valor
    `None` elimina el claim (p. ej. `exp=None` emite un token sin expiración).
    """
    payload: dict[str, object] = {
        "sub": user,
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    payload.update(overrides)
    payload = {k: v for k, v in payload.items() if v is not None}
    return jwt.encode(payload, secret, algorithm="HS256")


def auth_headers(user: str = "user-1") -> dict[str, str]:
    """Cabecera Authorization con un token válido para `user`."""
    return {"Authorization": f"Bearer {make_token(user)}"}
