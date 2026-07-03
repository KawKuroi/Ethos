"""Tests de la protección de la API contra abuso (middlewares y factory)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ethos_api.config import settings
from ethos_api.main import create_app


def _app(monkeypatch: pytest.MonkeyPatch, **overrides: object) -> FastAPI:
    for campo, valor in overrides.items():
        monkeypatch.setattr(settings, campo, valor)
    return create_app()


def test_rate_limit_devuelve_429_con_retry_after(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app(monkeypatch, rate_limit_per_minute=3)
    with TestClient(app) as client:
        for _ in range(3):
            assert client.get("/credentials").status_code == 401
        respuesta = client.get("/credentials")
    assert respuesta.status_code == 429
    assert int(respuesta.headers["retry-after"]) >= 1


def test_health_exento_del_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, rate_limit_per_minute=2)
    with TestClient(app) as client:
        for _ in range(6):
            assert client.get("/health").status_code == 200


def test_cuerpo_grande_devuelve_413(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, max_body_bytes=100)
    with TestClient(app) as client:
        respuesta = client.post("/credentials", content=b"x" * 200)
    assert respuesta.status_code == 413


def test_cors_permite_el_origen_de_la_web(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, allowed_origins="https://ethos-steel.vercel.app")
    with TestClient(app) as client:
        respuesta = client.options(
            "/credentials",
            headers={
                "Origin": "https://ethos-steel.vercel.app",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert respuesta.status_code == 200
    assert (
        respuesta.headers["access-control-allow-origin"]
        == "https://ethos-steel.vercel.app"
    )


def test_cors_niega_otros_origenes(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, allowed_origins="https://ethos-steel.vercel.app")
    with TestClient(app) as client:
        respuesta = client.options(
            "/credentials",
            headers={
                "Origin": "https://evil.example",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert respuesta.status_code == 400


def test_host_no_confiable_devuelve_400(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, allowed_hosts="testserver")
    with TestClient(app) as client:
        ok = client.get("/health")
        malo = client.get("/health", headers={"host": "evil.example"})
    assert ok.status_code == 200
    assert malo.status_code == 400


def test_cabeceras_de_seguridad_presentes(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch)
    with TestClient(app) as client:
        respuesta = client.get("/health")
    assert respuesta.headers["x-content-type-options"] == "nosniff"
    assert respuesta.headers["x-frame-options"] == "DENY"
    assert respuesta.headers["referrer-policy"] == "no-referrer"
    assert "strict-transport-security" in respuesta.headers


def test_docs_apagados_en_produccion(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, environment="production")
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_docs_disponibles_en_desarrollo(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch, environment="development")
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 200
