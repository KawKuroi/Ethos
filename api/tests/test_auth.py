"""Tests de la verificación del JWT de sesión."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from ethos_api import auth
from ethos_api.config import settings

_SECRET = "clave-de-prueba-para-jwt-de-al-menos-32-bytes"


def _token(secret: str = _SECRET, **overrides: object) -> str:
    payload: dict[str, object] = {
        "sub": "user-123",
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    payload.update(overrides)
    return jwt.encode(payload, secret, algorithm="HS256")


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_token_valido(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "supabase_jwt_secret", _SECRET)
    assert auth.get_current_user_id(_creds(_token())) == "user-123"


def test_sin_token() -> None:
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user_id(None)
    assert exc.value.status_code == 401


def test_firma_invalida(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "supabase_jwt_secret", _SECRET)
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user_id(_creds(_token(secret="otra-clave-distinta-igual-de-larga-de-32-bytes")))
    assert exc.value.status_code == 401
