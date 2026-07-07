"""Fixtures compartidas de la suite."""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from ethos_api.config import settings
from ethos_api.main import app
from ethos_api.middleware import RateLimitMiddleware
from tests.helpers import JWT_SECRET


@pytest.fixture(autouse=True)
def reset_rate_limit() -> None:
    """Limpia la ventana del rate limit entre tests.

    Todos los requests del TestClient comparten la IP "testclient"; con la
    suite ya por encima de 120 peticiones, sin este reset el limitador
    devolvería 429 a mitad de suite.
    """
    stack: object | None = getattr(app, "middleware_stack", None)
    while stack is not None:
        if isinstance(stack, RateLimitMiddleware):
            stack._hits.clear()
            break
        stack = getattr(stack, "app", None)


@pytest.fixture
def anyio_backend() -> str:
    """Backend de anyio para tests async (solo asyncio; trio no está instalado)."""
    return "asyncio"


@pytest.fixture
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    """Configura el secreto JWT legacy en settings y lo devuelve."""
    monkeypatch.setattr(settings, "supabase_jwt_secret", SecretStr(JWT_SECRET))
    return JWT_SECRET
