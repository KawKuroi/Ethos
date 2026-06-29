"""Servidor MCP de Ethos (FastMCP).

Se monta dentro del backend FastAPI para mantener un único servicio vivo
(API + MCP). El transporte streamable-HTTP se configura sin estado de sesión en
memoria (`stateless_http=True`) al construir el app ASGI en `main.py`, para
poder escalar sin afinidad de sesión.
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp: FastMCP = FastMCP(name="Ethos")


@mcp.tool
def ping() -> str:
    """Tool de prueba para verificar la conexión con el servidor MCP."""
    return "pong"
