"""Repositorio de credenciales: contrato e implementación en memoria."""

from __future__ import annotations

from typing import Protocol

from ethos_api.credentials.models import UserCredential


class CredentialRepository(Protocol):
    """Persistencia de credenciales por usuario y proveedor."""

    def upsert(self, credential: UserCredential) -> None: ...

    def list_for_user(self, user_id: str) -> list[UserCredential]: ...

    def get(self, user_id: str, provider: str) -> UserCredential | None: ...

    def delete(self, user_id: str, provider: str) -> bool: ...


class InMemoryCredentialRepository:
    """Implementación en memoria (no persistente).

    Útil para tests y desarrollo. El repositorio respaldado por Supabase
    (con su estrategia de RLS) llega en el siguiente ciclo.
    """

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
