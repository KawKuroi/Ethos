"""Dependencias del flujo OAuth del MCP (singletons inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.oauth.store import (
    InMemoryCodeStore,
    InMemoryOAuthClientStore,
    InMemoryOAuthTokenStore,
    OAuthClientStore,
    OAuthTokenStore,
    SupabaseOAuthClientStore,
    SupabaseOAuthTokenStore,
)
from ethos_api.supabase_rest import get_rest

_clients: OAuthClientStore | None = None
_tokens: OAuthTokenStore | None = None
_codes: InMemoryCodeStore | None = None


def get_oauth_client_store() -> OAuthClientStore:
    global _clients
    if _clients is None:
        rest = get_rest()
        _clients = SupabaseOAuthClientStore(rest) if rest else InMemoryOAuthClientStore()
    return _clients


def get_oauth_token_store() -> OAuthTokenStore:
    global _tokens
    if _tokens is None:
        rest = get_rest()
        _tokens = SupabaseOAuthTokenStore(rest) if rest else InMemoryOAuthTokenStore()
    return _tokens


def get_code_store() -> InMemoryCodeStore:
    """Los códigos son efímeros por diseño: siempre en memoria."""
    global _codes
    if _codes is None:
        _codes = InMemoryCodeStore()
    return _codes


ClientStoreDep = Annotated[OAuthClientStore, Depends(get_oauth_client_store)]
TokenStoreDep = Annotated[OAuthTokenStore, Depends(get_oauth_token_store)]
CodeStoreDep = Annotated[InMemoryCodeStore, Depends(get_code_store)]
