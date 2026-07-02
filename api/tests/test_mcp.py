"""Verifica el servidor MCP: montaje HTTP y roundtrip real del tool `ping`."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from fastmcp import Client

from ethos_api.main import app
from ethos_api.mcp_server import mcp


def test_mcp_endpoint_montado() -> None:
    # El contexto del TestClient ejecuta el lifespan del MCP.
    with TestClient(app) as client:
        respuesta = client.get("/mcp/")
    # La ruta existe (no 404). Puede responder 4xx por falta de cabeceras de
    # streamable-HTTP, pero confirma que el MCP está montado.
    assert respuesta.status_code != 404


@pytest.mark.anyio
async def test_ping_responde() -> None:
    # Cliente in-memory de FastMCP: ejercita el tool de verdad, sin red.
    async with Client(mcp) as client:
        resultado = await client.call_tool("ping")
    assert resultado.data == "pong"
