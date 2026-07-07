"""Middlewares ASGI de protección de la API contra abuso.

ASGI puro (sin BaseHTTPMiddleware) para no interferir con el streaming SSE
del transporte del MCP. El estado vive en memoria: suficiente con una sola
instancia (Render free); con varias réplicas se sustituye por un backend
compartido (p. ej. Redis).
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]

# Máximo de IPs recordadas por el limitador antes de podar entradas vacías.
_MAX_TRACKED_IPS = 10_000


async def _plain_response(
    send: Send,
    status: int,
    body: bytes,
    extra_headers: list[tuple[bytes, bytes]] | None = None,
) -> None:
    headers = [(b"content-type", b"text/plain; charset=utf-8")]
    if extra_headers:
        headers.extend(extra_headers)
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


class SecurityHeadersMiddleware:
    """Añade cabeceras de seguridad estándar a toda respuesta HTTP."""

    _HEADERS: tuple[tuple[bytes, bytes], ...] = (
        (b"x-content-type-options", b"nosniff"),
        (b"x-frame-options", b"DENY"),
        (b"referrer-policy", b"no-referrer"),
        (b"strict-transport-security", b"max-age=63072000; includeSubDomains"),
    )

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), *self._HEADERS]
            await send(message)

        await self.app(scope, receive, send_with_headers)


class BodySizeLimitMiddleware:
    """Rechaza cuerpos de petición mayores al límite.

    Content-Length mayor al límite → 413 inmediato. Cuerpos chunked (sin
    Content-Length) se cortan simulando la desconexión del cliente cuando
    exceden el límite. Las rutas de import de archivos (`/imports` y
    `/sources/*/import`) usan un límite mayor propio (D49) sin aflojar el
    del resto de la API.
    """

    def __init__(
        self, app: ASGIApp, max_bytes: int, import_max_bytes: int | None = None
    ) -> None:
        self.app = app
        self.max_bytes = max_bytes
        self.import_max_bytes = import_max_bytes or max_bytes

    def _limit_for(self, path: str) -> int:
        if path == "/imports" or (
            path.startswith("/sources/") and path.endswith("/import")
        ):
            return self.import_max_bytes
        return self.max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        limit = self._limit_for(str(scope.get("path", "")))
        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                if int(content_length) > limit:
                    await _plain_response(send, 413, b"Cuerpo demasiado grande")
                    return
            except ValueError:
                await _plain_response(send, 400, b"Content-Length invalido")
                return

        received = 0

        async def capped_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    return {"type": "http.disconnect"}
            return message

        await self.app(scope, capped_receive, send)


class McpAuthChallengeMiddleware:
    """Desafío OAuth 2.1 en el transporte del MCP (D56).

    Una petición a `/mcp` sin Bearer resoluble (legacy `eth_live_` u OAuth
    `eth_oauth_`) recibe 401 con `WWW-Authenticate` apuntando a la metadata
    del recurso protegido (RFC 9728), que dispara el flujo OAuth en los
    clientes MCP. El resolver se inyecta para testear sin stores reales.
    """

    def __init__(
        self, app: ASGIApp, resolver: Callable[[str | None], str | None]
    ) -> None:
        self.app = app
        self.resolver = resolver

    @staticmethod
    def _metadata_url(scope: Scope) -> str:
        from ethos_api.config import settings

        if settings.public_base_url:
            base = settings.public_base_url.rstrip("/")
        else:
            headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
            scheme = headers.get("x-forwarded-proto", scope.get("scheme", "http"))
            base = f"{scheme}://{headers.get('host', 'localhost')}"
        return f"{base}/.well-known/oauth-protected-resource/mcp"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = str(scope.get("path", ""))
        # Solo el transporte del MCP (/mcp y /mcp/…); no rutas como /mcp-token.
        if scope["type"] != "http" or not (path == "/mcp" or path.startswith("/mcp/")):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        authorization = headers.get(b"authorization")
        header_value = authorization.decode() if authorization else None
        if self.resolver(header_value) is None:
            challenge = (
                f'Bearer resource_metadata="{self._metadata_url(scope)}"'.encode()
            )
            await _plain_response(
                send,
                401,
                b"No autenticado: token del MCP requerido",
                [(b"www-authenticate", challenge)],
            )
            return
        await self.app(scope, receive, send)


class RateLimitMiddleware:
    """Límite de peticiones por IP con ventana deslizante en memoria.

    Al exceder el límite responde 429 con Retry-After. `/health` queda exento
    para no pelear con el keep-alive.
    """

    def __init__(
        self,
        app: ASGIApp,
        limit_per_minute: int,
        exempt_paths: frozenset[str] = frozenset({"/health"}),
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.app = app
        self.limit = limit_per_minute
        self.window = 60.0
        self.exempt_paths = exempt_paths
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}

    def _prune(self, now: float) -> None:
        # Evita crecer sin límite: poda IPs sin actividad en la ventana.
        if len(self._hits) <= _MAX_TRACKED_IPS:
            return
        for ip in list(self._hits):
            hits = self._hits[ip]
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if not hits:
                del self._hits[ip]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or self.limit <= 0
            or scope.get("path") in self.exempt_paths
        ):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        ip = client[0] if client else "unknown"
        now = self._clock()
        self._prune(now)
        hits = self._hits.setdefault(ip, deque())
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            retry_after = max(1, int(self.window - (now - hits[0])) + 1)
            await _plain_response(
                send,
                429,
                b"Demasiadas peticiones",
                [(b"retry-after", str(retry_after).encode())],
            )
            return
        hits.append(now)
        await self.app(scope, receive, send)
