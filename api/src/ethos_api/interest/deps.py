"""Dependencia del repositorio de interés.

Respaldo Supabase cuando está configurado; memoria en tests y desarrollo.
Los tests lo sustituyen con `dependency_overrides`.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.interest.repository import (
    InMemoryInterestRepository,
    InterestRepository,
    SupabaseInterestRepository,
)
from ethos_api.supabase_rest import get_rest

_repository: InterestRepository | None = None


def get_repository() -> InterestRepository:
    global _repository
    if _repository is None:
        rest = get_rest()
        _repository = (
            SupabaseInterestRepository(rest) if rest else InMemoryInterestRepository()
        )
    return _repository


RepositoryDep = Annotated[InterestRepository, Depends(get_repository)]
