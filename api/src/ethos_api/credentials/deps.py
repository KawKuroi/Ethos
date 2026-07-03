"""Dependencia del repositorio de credenciales.

Elige el respaldo Supabase cuando está configurado (D35); si no, memoria
(tests y desarrollo). Los tests lo sustituyen con `dependency_overrides`.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.credentials.repository import (
    CredentialRepository,
    InMemoryCredentialRepository,
    SupabaseCredentialRepository,
)
from ethos_api.supabase_rest import get_rest

_repository: CredentialRepository | None = None


def get_repository() -> CredentialRepository:
    global _repository
    if _repository is None:
        rest = get_rest()
        _repository = (
            SupabaseCredentialRepository(rest) if rest else InMemoryCredentialRepository()
        )
    return _repository


RepositoryDep = Annotated[CredentialRepository, Depends(get_repository)]
