"""Dependencia del repositorio de feedback (Supabase o memoria)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.feedback.repository import (
    FeedbackRepository,
    InMemoryFeedbackRepository,
    SupabaseFeedbackRepository,
)
from ethos_api.supabase_rest import get_rest

_repository: FeedbackRepository | None = None


def get_repository() -> FeedbackRepository:
    global _repository
    if _repository is None:
        rest = get_rest()
        _repository = (
            SupabaseFeedbackRepository(rest) if rest else InMemoryFeedbackRepository()
        )
    return _repository


RepositoryDep = Annotated[FeedbackRepository, Depends(get_repository)]
