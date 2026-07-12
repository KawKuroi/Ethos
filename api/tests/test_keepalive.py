"""Verifica el toque de keep-alive a la BD (throttle, fallos y /health)."""

from __future__ import annotations

from typing import Any, cast

from fastapi.testclient import TestClient

from ethos_api import keepalive
from ethos_api.keepalive import DbKeepalive
from ethos_api.main import app
from ethos_api.supabase_rest import SupabaseRest, SupabaseRestError


class FakeRest:
    """Doble del cliente PostgREST que cuenta las consultas."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, dict[str, str]]] = []

    def select(self, table: str, params: dict[str, str]) -> list[dict[str, Any]]:
        self.calls.append((table, params))
        if self.fail:
            raise SupabaseRestError("PostgREST respondió 500")
        return []


class FakeClock:
    """Reloj monotónico controlable desde el test."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _keepalive(rest: FakeRest | None, clock: FakeClock) -> DbKeepalive:
    return DbKeepalive(
        interval_seconds=3600.0,
        rest_provider=lambda: cast(SupabaseRest | None, rest),
        clock=clock,
    )


def test_primer_toque_consulta_la_bd() -> None:
    rest = FakeRest()
    ka = _keepalive(rest, FakeClock())
    assert ka.touch_if_due() == "touched"
    assert rest.calls == [("source_state", {"select": "user_id", "limit": "1"})]


def test_dentro_del_intervalo_no_repite() -> None:
    rest = FakeRest()
    clock = FakeClock()
    ka = _keepalive(rest, clock)
    ka.touch_if_due()
    clock.advance(1800.0)
    assert ka.touch_if_due() == "skipped"
    assert len(rest.calls) == 1


def test_vencido_el_intervalo_vuelve_a_tocar() -> None:
    rest = FakeRest()
    clock = FakeClock()
    ka = _keepalive(rest, clock)
    ka.touch_if_due()
    clock.advance(3600.0)
    assert ka.touch_if_due() == "touched"
    assert len(rest.calls) == 2


def test_sin_supabase_queda_deshabilitado() -> None:
    ka = _keepalive(None, FakeClock())
    assert ka.touch_if_due() == "disabled"


def test_fallo_de_postgrest_no_propaga() -> None:
    rest = FakeRest(fail=True)
    ka = _keepalive(rest, FakeClock())
    assert ka.touch_if_due() == "error"


def test_tras_fallo_no_reintenta_en_rafaga() -> None:
    rest = FakeRest(fail=True)
    clock = FakeClock()
    ka = _keepalive(rest, clock)
    ka.touch_if_due()
    clock.advance(60.0)
    assert ka.touch_if_due() == "skipped"
    assert len(rest.calls) == 1


def test_health_dispara_el_toque_en_segundo_plano(monkeypatch: Any) -> None:
    llamadas: list[str] = []

    def falso_toque() -> str:
        llamadas.append("toque")
        return "touched"

    monkeypatch.setattr(keepalive.db_keepalive, "touch_if_due", falso_toque)
    with TestClient(app) as client:
        respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "ok"
    assert llamadas == ["toque"]
