"""Tests de la verificación del JWT de sesión."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from ethos_api import auth
from tests.helpers import make_token


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _assert_401(token: str) -> None:
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user_id(_creds(token))
    assert exc.value.status_code == 401


def test_token_valido(jwt_secret: str) -> None:
    assert auth.get_current_user_id(_creds(make_token("user-123"))) == "user-123"


def test_sin_token() -> None:
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user_id(None)
    assert exc.value.status_code == 401


def test_firma_invalida(jwt_secret: str) -> None:
    _assert_401(make_token(secret="otra-clave-distinta-igual-de-larga-de-32-bytes"))


def test_token_expirado(jwt_secret: str) -> None:
    _assert_401(make_token(exp=datetime.now(UTC) - timedelta(minutes=1)))


def test_sin_expiracion(jwt_secret: str) -> None:
    # `exp` es obligatorio: un token sin expiración se rechaza.
    _assert_401(make_token(exp=None))


def test_audience_incorrecta(jwt_secret: str) -> None:
    _assert_401(make_token(aud="otra-audiencia"))


def test_sin_sujeto(jwt_secret: str) -> None:
    _assert_401(make_token(sub=None))


def test_asimetrico_sin_supabase_url(jwt_secret: str) -> None:
    # Un token ES256 exige verificación JWKS; sin SUPABASE_URL se rechaza.
    private_key = ec.generate_private_key(ec.SECP256R1())
    token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated", "exp": datetime.now(UTC) + timedelta(hours=1)},
        private_key,
        algorithm="ES256",
    )
    _assert_401(token)
