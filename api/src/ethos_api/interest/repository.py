"""Repositorio de la lista de interés: contrato, memoria y respaldo Supabase."""

from __future__ import annotations

from typing import Any, Protocol

from ethos_api.interest.models import CategoryInterest
from ethos_api.supabase_rest import SupabaseRest


class InterestRepository(Protocol):
    """Persistencia del interés en categorías en desarrollo."""

    def add(self, interest: CategoryInterest) -> None: ...

    def list_for_category(self, category: str) -> list[CategoryInterest]: ...


class SupabaseInterestRepository:
    """Respaldo en la tabla `category_interest` vía PostgREST (D50).

    Upsert idempotente por (email, category): registrarse dos veces no duplica.
    """

    _TABLE = "category_interest"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    @staticmethod
    def _to_model(row: dict[str, Any]) -> CategoryInterest:
        return CategoryInterest(
            email=row["email"],
            category=row["category"],
            user_id=row.get("user_id"),
            created_at=row["created_at"],
        )

    def add(self, interest: CategoryInterest) -> None:
        self._rest.upsert(
            self._TABLE,
            [
                {
                    "email": interest.email,
                    "category": interest.category,
                    "user_id": interest.user_id,
                    "created_at": interest.created_at.isoformat(),
                }
            ],
            on_conflict="email,category",
        )

    def list_for_category(self, category: str) -> list[CategoryInterest]:
        rows = self._rest.select(self._TABLE, {"category": f"eq.{category}"})
        return [self._to_model(row) for row in rows]


class InMemoryInterestRepository:
    """Implementación en memoria (tests y desarrollo)."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], CategoryInterest] = {}

    def add(self, interest: CategoryInterest) -> None:
        self._store[(interest.email, interest.category)] = interest

    def list_for_category(self, category: str) -> list[CategoryInterest]:
        return [i for (_, cat), i in self._store.items() if cat == category]
