"""Tests del borrado de datos y de cuenta diferido (D53)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from ethos_api.account import service
from ethos_api.account.deps import get_account_rest
from ethos_api.main import app
from ethos_api.supabase_rest import SupabaseRest
from tests.helpers import auth_headers, make_token


class FakePostgrest:
    """MockTransport que registra peticiones y responde según método/tabla."""

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.requests: list[httpx.Request] = []
        self._responses = responses or {}

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        table = request.url.path.rsplit("/", 1)[-1]
        if request.method == "GET":
            return httpx.Response(200, json=self._responses.get(table, []))
        if request.method == "DELETE":
            return httpx.Response(200, json=self._responses.get(f"del:{table}", []))
        return httpx.Response(201, json=[])

    def methods_for(self, table: str) -> list[str]:
        return [r.method for r in self.requests if r.url.path.endswith(f"/{table}")]


def _rest(fake: FakePostgrest) -> SupabaseRest:
    client = httpx.Client(
        transport=httpx.MockTransport(fake), base_url="https://proj.supabase.co/rest/v1"
    )
    return SupabaseRest("https://proj.supabase.co", "service-key", client=client)


@pytest.fixture
def client(jwt_secret: str) -> Iterator[tuple[TestClient, FakePostgrest]]:
    fake = FakePostgrest()
    app.dependency_overrides[get_account_rest] = lambda: _rest(fake)
    with TestClient(app) as test_client:
        yield test_client, fake
    app.dependency_overrides.clear()


def test_eliminar_datos_borra_las_tablas_de_contexto(
    client: tuple[TestClient, FakePostgrest],
) -> None:
    test_client, fake = client
    respuesta = test_client.delete("/account/data", headers=auth_headers())
    assert respuesta.status_code == 204
    for table in ("user_items", "user_events", "source_state", "user_credentials"):
        assert "DELETE" in fake.methods_for(table)


def test_programar_borrado_devuelve_fecha(
    client: tuple[TestClient, FakePostgrest],
) -> None:
    test_client, _ = client
    respuesta = test_client.post("/account/deletion", headers=auth_headers())
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["scheduled"] is True
    assert datos["purge_after"] is not None


def test_estado_sin_programacion(
    client: tuple[TestClient, FakePostgrest],
) -> None:
    test_client, _ = client
    respuesta = test_client.get("/account/deletion", headers=auth_headers())
    assert respuesta.json() == {"scheduled": False, "purge_after": None}


def test_estado_con_programacion(
    client: tuple[TestClient, FakePostgrest],
) -> None:
    now = datetime.now(UTC)
    fake = FakePostgrest(
        {
            "account_deletions": [
                {
                    "requested_at": now.isoformat(),
                    "purge_after": (now + timedelta(days=30)).isoformat(),
                }
            ]
        }
    )
    app.dependency_overrides[get_account_rest] = lambda: _rest(fake)
    respuesta = TestClient(app).get("/account/deletion", headers=auth_headers())
    assert respuesta.json()["scheduled"] is True
    app.dependency_overrides.clear()


def test_deshacer_borra_la_marca(client: tuple[TestClient, FakePostgrest]) -> None:
    test_client, fake = client
    respuesta = test_client.delete("/account/deletion", headers=auth_headers())
    assert respuesta.status_code == 204
    assert "DELETE" in fake.methods_for("account_deletions")


def test_requiere_autenticacion(client: tuple[TestClient, FakePostgrest]) -> None:
    test_client, _ = client
    assert test_client.delete("/account/data").status_code == 401


def test_503_sin_supabase(jwt_secret: str) -> None:
    # Sin override: get_account_rest usa get_rest() real, que es None en tests.
    respuesta = TestClient(app).delete("/account/data", headers=auth_headers())
    assert respuesta.status_code == 503


def test_purga_borra_usuarios_vencidos() -> None:
    now = datetime.now(UTC)
    fake = FakePostgrest({"account_deletions": [{"user_id": "user-a"}, {"user_id": "user-b"}]})
    borrados: list[str] = []
    purgadas = service.purge_due_accounts(
        _rest(fake), borrados.append, now=now
    )
    assert purgadas == 2
    assert borrados == ["user-a", "user-b"]


def test_email_se_toma_del_jwt(client: tuple[TestClient, FakePostgrest]) -> None:
    # El aviso usa el claim email; aquí solo comprobamos que el endpoint lo
    # acepta y responde (el envío es best-effort en segundo plano).
    test_client, _ = client
    token = make_token("user-1", email="leo@example.com")
    respuesta = test_client.post(
        "/account/deletion", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 200
