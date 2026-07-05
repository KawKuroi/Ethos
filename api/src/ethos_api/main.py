"""Aplicación FastAPI de Ethos: API HTTP y servidor MCP en un solo servicio."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from ethos_api.config import settings
from ethos_api.credentials.router import router as credentials_router
from ethos_api.games.router import router as games_router
from ethos_api.mcp_auth import router as mcp_token_router
from ethos_api.mcp_server import mcp
from ethos_api.middleware import (
    BodySizeLimitMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from ethos_api.music.router import router as music_router


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def create_app() -> FastAPI:
    """Construye la aplicación con su pila de protección.

    Factory para poder crear apps con settings distintos en tests.
    """
    # El app del MCP trae su propio lifespan; debe pasarse a FastAPI para que
    # inicialice correctamente el gestor de sesiones del MCP. El transporte se
    # configura sin estado (stateless_http) para escalar sin afinidad de sesión.
    mcp_app = mcp.http_app(path="/", stateless_http=True)

    is_production = settings.environment == "production"
    app = FastAPI(
        title="Ethos API",
        version="0.1.0",
        lifespan=mcp_app.lifespan,
        # Sin docs interactivos en producción: menos superficie expuesta.
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )

    # Un único servicio combina la API y el endpoint MCP (montado en /mcp).
    app.mount("/mcp", mcp_app)

    # Endpoints HTTP de la API (autenticados con la sesión de Supabase).
    app.include_router(credentials_router)
    app.include_router(games_router)
    app.include_router(music_router)
    app.include_router(mcp_token_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        """Sonda de salud para keep-alive y monitores de despliegue."""
        return {"status": "ok", "environment": settings.environment}

    # Pila de protección, de fuera hacia adentro:
    # SecurityHeaders → TrustedHost → CORS → BodyLimit → RateLimit → app.
    # (add_middleware antepone: el último añadido queda más afuera.)
    app.add_middleware(
        RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute
    )
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_body_bytes)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_split_csv(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if settings.allowed_hosts != "*":
        app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=_split_csv(settings.allowed_hosts)
        )
    app.add_middleware(SecurityHeadersMiddleware)
    return app


app = create_app()
