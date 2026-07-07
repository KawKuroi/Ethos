"""Almacenes del flujo OAuth del MCP: clientes, códigos y tokens (D56).

Clientes y tokens persisten en Supabase (migración 0008) con espejo en
memoria para tests y desarrollo. Los authorization codes viven solo en
memoria: expiran a los 10 minutos y son de un solo uso; un redeploy pierde
los pendientes y el cliente simplemente reintenta el flujo.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from ethos_api.oauth.models import AuthorizationCode, OAuthClient
from ethos_api.supabase_rest import SupabaseRest

ACCESS_PREFIX = "eth_oauth_"
REFRESH_PREFIX = "eth_refresh_"

ACCESS_TTL = timedelta(days=30)
REFRESH_TTL = timedelta(days=90)
CODE_TTL = timedelta(minutes=10)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _now() -> datetime:
    return datetime.now(UTC)


class OAuthClientStore(Protocol):
    """Persistencia de clientes registrados dinámicamente."""

    def register(self, client_name: str, redirect_uris: list[str]) -> OAuthClient: ...

    def get(self, client_id: str) -> OAuthClient | None: ...


class OAuthTokenStore(Protocol):
    """Persistencia de tokens de acceso y refresh (solo hashes)."""

    def issue_pair(self, user_id: str, client_id: str) -> tuple[str, str, int]: ...

    def resolve_access(self, token: str) -> str | None: ...

    def consume_refresh(self, token: str) -> tuple[str, str] | None: ...

    def revoke(self, token: str) -> None: ...


class SupabaseOAuthClientStore:
    """Respaldo en la tabla `oauth_clients` (migración 0008)."""

    _TABLE = "oauth_clients"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def register(self, client_name: str, redirect_uris: list[str]) -> OAuthClient:
        client = OAuthClient(
            client_id="eth_client_" + secrets.token_urlsafe(12),
            client_name=client_name,
            redirect_uris=redirect_uris,
        )
        self._rest.insert(
            self._TABLE,
            [
                {
                    "client_id": client.client_id,
                    "client_name": client.client_name,
                    "redirect_uris": client.redirect_uris,
                }
            ],
        )
        return client

    def get(self, client_id: str) -> OAuthClient | None:
        rows = self._rest.select(
            self._TABLE, {"client_id": f"eq.{client_id}", "limit": "1"}
        )
        if not rows:
            return None
        row = rows[0]
        return OAuthClient(
            client_id=row["client_id"],
            client_name=row["client_name"],
            redirect_uris=list(row["redirect_uris"]),
        )


class InMemoryOAuthClientStore:
    """Implementación en memoria (tests y desarrollo)."""

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClient] = {}

    def register(self, client_name: str, redirect_uris: list[str]) -> OAuthClient:
        client = OAuthClient(
            client_id="eth_client_" + secrets.token_urlsafe(12),
            client_name=client_name,
            redirect_uris=redirect_uris,
        )
        self._clients[client.client_id] = client
        return client

    def get(self, client_id: str) -> OAuthClient | None:
        return self._clients.get(client_id)


class SupabaseOAuthTokenStore:
    """Respaldo en la tabla `oauth_tokens` (migración 0008)."""

    _TABLE = "oauth_tokens"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def issue_pair(self, user_id: str, client_id: str) -> tuple[str, str, int]:
        access = ACCESS_PREFIX + secrets.token_urlsafe(24)
        refresh = REFRESH_PREFIX + secrets.token_urlsafe(24)
        now = _now()
        self._rest.insert(
            self._TABLE,
            [
                self._row(access, user_id, client_id, "access", now + ACCESS_TTL),
                self._row(refresh, user_id, client_id, "refresh", now + REFRESH_TTL),
            ],
        )
        return access, refresh, int(ACCESS_TTL.total_seconds())

    @staticmethod
    def _row(
        token: str, user_id: str, client_id: str, kind: str, expires_at: datetime
    ) -> dict[str, Any]:
        return {
            "token_hash": _hash(token),
            "user_id": user_id,
            "client_id": client_id,
            "kind": kind,
            "expires_at": expires_at.isoformat(),
        }

    def _lookup(self, token: str, kind: str) -> dict[str, Any] | None:
        rows = self._rest.select(
            self._TABLE,
            {
                "token_hash": f"eq.{_hash(token)}",
                "kind": f"eq.{kind}",
                "select": "user_id,client_id,expires_at",
                "limit": "1",
            },
        )
        if not rows:
            return None
        row = rows[0]
        if datetime.fromisoformat(row["expires_at"]) < _now():
            return None
        return row

    def resolve_access(self, token: str) -> str | None:
        if not token.startswith(ACCESS_PREFIX):
            return None
        row = self._lookup(token, "access")
        return row["user_id"] if row else None

    def consume_refresh(self, token: str) -> tuple[str, str] | None:
        if not token.startswith(REFRESH_PREFIX):
            return None
        row = self._lookup(token, "refresh")
        if row is None:
            return None
        # Rotación: el refresh usado se invalida al momento.
        self._rest.delete(self._TABLE, {"token_hash": f"eq.{_hash(token)}"})
        return row["user_id"], row["client_id"]

    def revoke(self, token: str) -> None:
        """Revocación RFC 7009: borra el token (access o refresh) si existe."""
        if not token.startswith((ACCESS_PREFIX, REFRESH_PREFIX)):
            return
        self._rest.delete(self._TABLE, {"token_hash": f"eq.{_hash(token)}"})


class InMemoryOAuthTokenStore:
    """Implementación en memoria (tests y desarrollo)."""

    def __init__(self) -> None:
        # hash → (user_id, client_id, kind, expires_at)
        self._tokens: dict[str, tuple[str, str, str, datetime]] = {}

    def issue_pair(self, user_id: str, client_id: str) -> tuple[str, str, int]:
        access = ACCESS_PREFIX + secrets.token_urlsafe(24)
        refresh = REFRESH_PREFIX + secrets.token_urlsafe(24)
        now = _now()
        self._tokens[_hash(access)] = (user_id, client_id, "access", now + ACCESS_TTL)
        self._tokens[_hash(refresh)] = (user_id, client_id, "refresh", now + REFRESH_TTL)
        return access, refresh, int(ACCESS_TTL.total_seconds())

    def resolve_access(self, token: str) -> str | None:
        if not token.startswith(ACCESS_PREFIX):
            return None
        entry = self._tokens.get(_hash(token))
        if entry is None or entry[2] != "access" or entry[3] < _now():
            return None
        return entry[0]

    def consume_refresh(self, token: str) -> tuple[str, str] | None:
        if not token.startswith(REFRESH_PREFIX):
            return None
        entry = self._tokens.pop(_hash(token), None)
        if entry is None or entry[2] != "refresh" or entry[3] < _now():
            return None
        return entry[0], entry[1]

    def revoke(self, token: str) -> None:
        """Revocación RFC 7009: borra el token (access o refresh) si existe."""
        self._tokens.pop(_hash(token), None)


class InMemoryCodeStore:
    """Authorization codes de un solo uso, en memoria (efímeros por diseño)."""

    def __init__(self) -> None:
        self._codes: dict[str, AuthorizationCode] = {}

    def mint(
        self,
        user_id: str,
        client_id: str,
        redirect_uri: str,
        code_challenge: str,
        scope: str,
    ) -> str:
        code = secrets.token_urlsafe(32)
        self._codes[code] = AuthorizationCode(
            user_id=user_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            scope=scope,
            expires_at=_now() + CODE_TTL,
        )
        return code

    def consume(self, code: str) -> AuthorizationCode | None:
        grant = self._codes.pop(code, None)
        if grant is None or grant.expires_at < _now():
            return None
        return grant
