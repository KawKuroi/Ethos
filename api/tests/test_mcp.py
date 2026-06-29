"""Verifica que el servidor MCP está montado en /mcp."""

from __future__ import annotations

from fastapi.testclient import TestClient

from ethos_api.main import app


def test_mcp_endpoint_montado() -> None:
    # El contexto del TestClient ejecuta el lifespan del MCP.
    with TestClient(app) as client:
        respuesta = client.get("/mcp/")
    # La ruta existe (no 404). Puede responder 4xx por falta de cabeceras de
    # streamable-HTTP, pero confirma que el MCP está montado.
    assert respuesta.status_code != 404
