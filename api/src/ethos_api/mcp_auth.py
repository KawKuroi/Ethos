"""Auth del MCP por token de usuario (D22).

La IA se autentica ante el MCP con un token opaco `eth_live_…` emitido con la
sesión de Supabase. Solo se guarda su hash SHA-256 (en memoria hasta la
migración a Supabase, D35); el token en claro se muestra una única vez. Ese
token nunca se reenvía a APIs de terceros (regla de `global.md`).
"""

from __future__ import annotations

import hashlib
import secrets
from typing import Annotated, Protocol

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from ethos_api.auth import CurrentUserId
from ethos_api.supabase_rest import SupabaseRest, get_rest

_TOKEN_PREFIX = "eth_live_"  # noqa: S105 — prefijo público del token, no un secreto


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class McpTokenStore(Protocol):
    """Puerto de los tokens del MCP: un token activo por usuario, como hash."""

    def issue(self, user_id: str) -> str: ...

    def resolve(self, token: str) -> str | None: ...


def _new_token() -> str:
    return _TOKEN_PREFIX + secrets.token_urlsafe(24)


class SupabaseMcpTokenStore:
    """Respaldo en la tabla `mcp_tokens` (migración 0003, D35)."""

    _TABLE = "mcp_tokens"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def issue(self, user_id: str) -> str:
        token = _new_token()
        # PK = user_id: el upsert rota el token anterior del usuario.
        self._rest.upsert(
            self._TABLE,
            [{"user_id": user_id, "token_hash": _hash(token)}],
            on_conflict="user_id",
        )
        return token

    def resolve(self, token: str) -> str | None:
        if not token.startswith(_TOKEN_PREFIX):
            return None
        rows = self._rest.select(
            self._TABLE,
            {"token_hash": f"eq.{_hash(token)}", "select": "user_id", "limit": "1"},
        )
        return rows[0]["user_id"] if rows else None


class InMemoryMcpTokenStore:
    """Implementación en memoria, para tests y desarrollo."""

    def __init__(self) -> None:
        self._user_by_hash: dict[str, str] = {}
        self._hash_by_user: dict[str, str] = {}

    def issue(self, user_id: str) -> str:
        """Emite (y rota) el token del usuario; devuelve el claro una vez."""
        token = _new_token()
        digest = _hash(token)
        previous = self._hash_by_user.get(user_id)
        if previous:
            self._user_by_hash.pop(previous, None)
        self._hash_by_user[user_id] = digest
        self._user_by_hash[digest] = user_id
        return token

    def resolve(self, token: str) -> str | None:
        """Devuelve el usuario dueño del token, o None si no es válido."""
        if not token.startswith(_TOKEN_PREFIX):
            return None
        return self._user_by_hash.get(_hash(token))


_store: McpTokenStore | None = None


def get_mcp_token_store() -> McpTokenStore:
    """Supabase si está configurado; memoria en local/CI (D35)."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseMcpTokenStore(rest) if rest else InMemoryMcpTokenStore()
    return _store


def user_from_authorization(header: str | None, store: McpTokenStore) -> str | None:
    """Resuelve el usuario desde un header `Authorization: Bearer eth_live_…`."""
    if not header or not header.lower().startswith("bearer "):
        return None
    return store.resolve(header[7:].strip())


def resolve_bearer_user(header: str | None) -> str | None:
    """Resuelve el usuario de un Bearer legacy (`eth_live_`) u OAuth (`eth_oauth_`).

    Punto único de auth del MCP (D22/D56): lo usan las tools y el middleware
    del desafío 401. Import local para no acoplar este módulo al de OAuth.
    """
    if not header or not header.lower().startswith("bearer "):
        return None
    token = header[7:].strip()
    if token.startswith(_TOKEN_PREFIX):
        return get_mcp_token_store().resolve(token)
    from ethos_api.oauth.deps import get_oauth_token_store
    from ethos_api.oauth.store import ACCESS_PREFIX

    if token.startswith(ACCESS_PREFIX):
        return get_oauth_token_store().resolve_access(token)
    return None


class McpTokenOut(BaseModel):
    """Token emitido y endpoint del servidor MCP."""

    token: str
    endpoint: str


router = APIRouter(tags=["mcp"])

McpStoreDep = Annotated[McpTokenStore, Depends(get_mcp_token_store)]


@router.post("/mcp-token", response_model=McpTokenOut)
def issue_mcp_token(
    user_id: CurrentUserId, store: McpStoreDep, request: Request
) -> McpTokenOut:
    """Emite el token del MCP del usuario (rota el anterior)."""
    return McpTokenOut(
        token=store.issue(user_id),
        endpoint=str(request.base_url) + "mcp/",
    )
