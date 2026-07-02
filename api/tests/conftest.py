"""Fixtures compartidas de la suite."""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from ethos_api.config import settings
from tests.helpers import JWT_SECRET


@pytest.fixture
def anyio_backend() -> str:
    """Backend de anyio para tests async (solo asyncio; trio no está instalado)."""
    return "asyncio"


@pytest.fixture
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    """Configura el secreto JWT legacy en settings y lo devuelve."""
    monkeypatch.setattr(settings, "supabase_jwt_secret", SecretStr(JWT_SECRET))
    return JWT_SECRET
