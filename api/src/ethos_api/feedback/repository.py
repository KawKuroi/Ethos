"""Repositorio de feedback: contrato, memoria y respaldo Supabase (D52)."""

from __future__ import annotations

from typing import Any, Protocol

from ethos_api.feedback.models import FeedbackRecord
from ethos_api.supabase_rest import SupabaseRest


class FeedbackRepository(Protocol):
    """Persistencia de sugerencias y contacto."""

    def add(self, record: FeedbackRecord) -> None: ...

    def list_recent(self, limit: int = 50) -> list[FeedbackRecord]: ...


class SupabaseFeedbackRepository:
    """Respaldo en la tabla `feedback` vía PostgREST (RLS sin acceso público)."""

    _TABLE = "feedback"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    @staticmethod
    def _to_model(row: dict[str, Any]) -> FeedbackRecord:
        return FeedbackRecord(
            kind=row["kind"],
            message=row["message"],
            category=row.get("category"),
            name=row.get("name"),
            email=row.get("email"),
            user_id=row.get("user_id"),
            created_at=row["created_at"],
        )

    def add(self, record: FeedbackRecord) -> None:
        self._rest.insert(
            self._TABLE,
            [
                {
                    "kind": record.kind,
                    "message": record.message,
                    "category": record.category,
                    "name": record.name,
                    "email": record.email,
                    "user_id": record.user_id,
                    "created_at": record.created_at.isoformat(),
                }
            ],
        )

    def list_recent(self, limit: int = 50) -> list[FeedbackRecord]:
        rows = self._rest.select(
            self._TABLE, {"order": "created_at.desc", "limit": str(limit)}
        )
        return [self._to_model(row) for row in rows]


class InMemoryFeedbackRepository:
    """Implementación en memoria (tests y desarrollo)."""

    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []

    def add(self, record: FeedbackRecord) -> None:
        self._records.append(record)

    def list_recent(self, limit: int = 50) -> list[FeedbackRecord]:
        return list(reversed(self._records))[:limit]
