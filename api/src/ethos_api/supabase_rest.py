"""Cliente mínimo de PostgREST (Supabase) para los repositorios del backend.

El backend es la capa de confianza: autentica al usuario por JWT y acota cada
consulta por `user_id`, así que habla con PostgREST usando la service_role key
(los refrescos en segundo plano no tienen JWT del usuario). Las políticas RLS
owner-only de las tablas protegen el acceso directo de cualquier otro cliente.
"""

from __future__ import annotations

from typing import Any

import httpx

from ethos_api.config import settings


class SupabaseRestError(RuntimeError):
    """Error al consultar PostgREST."""


class SupabaseRest:
    """Operaciones básicas (select/upsert/delete) sobre PostgREST."""

    def __init__(
        self, base_url: str, service_key: str, *, client: httpx.Client | None = None
    ) -> None:
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
        }
        self._client = client or httpx.Client(
            base_url=f"{base_url.rstrip('/')}/rest/v1", headers=headers, timeout=15.0
        )

    def _check(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise SupabaseRestError(
                f"PostgREST respondió {response.status_code}: {response.text[:200]}"
            )

    def select(self, table: str, params: dict[str, str]) -> list[dict[str, Any]]:
        response = self._client.get(f"/{table}", params=params)
        self._check(response)
        data: Any = response.json()
        if not isinstance(data, list):
            raise SupabaseRestError(f"Respuesta inesperada de PostgREST en {table}")
        return data

    def upsert(
        self, table: str, rows: list[dict[str, Any]], *, on_conflict: str
    ) -> None:
        response = self._client.post(
            f"/{table}",
            params={"on_conflict": on_conflict},
            json=rows,
            headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
        )
        self._check(response)

    def insert(self, table: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        response = self._client.post(
            f"/{table}", json=rows, headers={"Prefer": "return=minimal"}
        )
        self._check(response)

    def delete(self, table: str, params: dict[str, str]) -> int:
        """Borra filas y devuelve cuántas eliminó."""
        response = self._client.delete(
            f"/{table}", params=params, headers={"Prefer": "return=representation"}
        )
        self._check(response)
        data: Any = response.json()
        return len(data) if isinstance(data, list) else 0


_rest: SupabaseRest | None = None


def get_rest() -> SupabaseRest | None:
    """Cliente PostgREST si Supabase está configurado; None en local/CI."""
    global _rest
    if _rest is None:
        url = settings.supabase_url
        key = settings.supabase_service_role_key.get_secret_value()
        if not url or not key:
            return None
        _rest = SupabaseRest(url, key)
    return _rest
