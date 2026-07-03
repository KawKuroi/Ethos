"""Auth del MCP por token de usuario (D22).

La IA se autentica ante el MCP con un token opaco `eth_live_…` emitido con la
sesión de Supabase. Solo se guarda su hash SHA-256 (en memoria hasta la
migración a Supabase, D35); el token en claro se muestra una única vez. Ese
token nunca se reenvía a APIs de terceros (regla de `global.md`).
"""

from __future__ import annotations

import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from ethos_api.auth import CurrentUserId

_TOKEN_PREFIX = "eth_live_"  # noqa: S105 — prefijo público del token, no un secreto


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class McpTokenStore:
    """Tokens del MCP: un token activo por usuario, guardado como hash."""

    def __init__(self) -> None:
        self._user_by_hash: dict[str, str] = {}
        self._hash_by_user: dict[str, str] = {}

    def issue(self, user_id: str) -> str:
        """Emite (y rota) el token del usuario; devuelve el claro una vez."""
        token = _TOKEN_PREFIX + secrets.token_urlsafe(24)
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


_store = McpTokenStore()


def get_mcp_token_store() -> McpTokenStore:
    return _store


def user_from_authorization(header: str | None, store: McpTokenStore) -> str | None:
    """Resuelve el usuario desde un header `Authorization: Bearer eth_live_…`."""
    if not header or not header.lower().startswith("bearer "):
        return None
    return store.resolve(header[7:].strip())


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
