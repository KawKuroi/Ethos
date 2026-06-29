"""Aplicación FastAPI de Ethos: API HTTP y servidor MCP en un solo servicio."""

from __future__ import annotations

from fastapi import FastAPI

from ethos_api.config import settings
from ethos_api.mcp_server import mcp

# El app del MCP trae su propio lifespan; debe pasarse a FastAPI para que
# inicialice correctamente el gestor de sesiones del MCP. El transporte se
# configura sin estado (stateless_http) para escalar sin afinidad de sesión.
mcp_app = mcp.http_app(path="/", stateless_http=True)

app = FastAPI(
    title="Ethos API",
    version="0.1.0",
    lifespan=mcp_app.lifespan,
)

# Un único servicio combina la API y el endpoint MCP (montado en /mcp).
app.mount("/mcp", mcp_app)


@app.get("/health")
def health() -> dict[str, str]:
    """Sonda de salud para keep-alive y monitores de despliegue."""
    return {"status": "ok", "environment": settings.environment}
