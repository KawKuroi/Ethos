"""Verifica el endpoint de salud."""

from __future__ import annotations

from fastapi.testclient import TestClient

from ethos_api.main import app

client = TestClient(app)


def test_health_ok() -> None:
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["status"] == "ok"
