"""Dependencia del repositorio de credenciales.

Hoy expone un singleton en memoria; al añadir el repositorio respaldado por
Supabase, solo cambia esta función (o se sustituye con `dependency_overrides`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.credentials.repository import (
    CredentialRepository,
    InMemoryCredentialRepository,
)

_repository: CredentialRepository = InMemoryCredentialRepository()


def get_repository() -> CredentialRepository:
    return _repository


RepositoryDep = Annotated[CredentialRepository, Depends(get_repository)]
