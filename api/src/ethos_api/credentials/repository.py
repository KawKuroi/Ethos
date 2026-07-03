"""Repositorio de credenciales: contrato, memoria y respaldo Supabase (D35)."""

from __future__ import annotations

from typing import Any, Protocol

from ethos_api.credentials.models import UserCredential
from ethos_api.supabase_rest import SupabaseRest


class CredentialRepository(Protocol):
    """Persistencia de credenciales por usuario y proveedor."""

    def upsert(self, credential: UserCredential) -> None: ...

    def list_for_user(self, user_id: str) -> list[UserCredential]: ...

    def get(self, user_id: str, provider: str) -> UserCredential | None: ...

    def delete(self, user_id: str, provider: str) -> bool: ...


class SupabaseCredentialRepository:
    """Respaldo en la tabla `user_credentials` vía PostgREST (RLS owner-only)."""

    _TABLE = "user_credentials"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    @staticmethod
    def _to_model(row: dict[str, Any]) -> UserCredential:
        return UserCredential(
            user_id=row["user_id"],
            provider=row["provider"],
            category=row["category"],
            encrypted_token=row["encrypted_token"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def upsert(self, credential: UserCredential) -> None:
        self._rest.upsert(
            self._TABLE,
            [
                {
                    "user_id": credential.user_id,
                    "provider": credential.provider,
                    "category": credential.category.value,
                    "encrypted_token": credential.encrypted_token,
                    "created_at": credential.created_at.isoformat(),
                    "updated_at": credential.updated_at.isoformat(),
                }
            ],
            on_conflict="user_id,provider",
        )

    def list_for_user(self, user_id: str) -> list[UserCredential]:
        rows = self._rest.select(self._TABLE, {"user_id": f"eq.{user_id}"})
        return [self._to_model(row) for row in rows]

    def get(self, user_id: str, provider: str) -> UserCredential | None:
        rows = self._rest.select(
            self._TABLE,
            {"user_id": f"eq.{user_id}", "provider": f"eq.{provider}", "limit": "1"},
        )
        return self._to_model(rows[0]) if rows else None

    def delete(self, user_id: str, provider: str) -> bool:
        deleted = self._rest.delete(
            self._TABLE, {"user_id": f"eq.{user_id}", "provider": f"eq.{provider}"}
        )
        return deleted > 0


class InMemoryCredentialRepository:
    """Implementación en memoria (no persistente), para tests y desarrollo."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], UserCredential] = {}

    def upsert(self, credential: UserCredential) -> None:
        self._store[(credential.user_id, credential.provider)] = credential

    def list_for_user(self, user_id: str) -> list[UserCredential]:
        return [c for (uid, _), c in self._store.items() if uid == user_id]

    def get(self, user_id: str, provider: str) -> UserCredential | None:
        return self._store.get((user_id, provider))

    def delete(self, user_id: str, provider: str) -> bool:
        return self._store.pop((user_id, provider), None) is not None
