"""Tests de sugerencias y contacto (D52)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from ethos_api.config import settings
from ethos_api.feedback import mailer
from ethos_api.feedback.deps import get_repository
from ethos_api.feedback.models import FeedbackRecord
from ethos_api.feedback.repository import InMemoryFeedbackRepository
from ethos_api.main import app
from tests.helpers import auth_headers


@pytest.fixture
def client(jwt_secret: str) -> Iterator[tuple[TestClient, InMemoryFeedbackRepository]]:
    repo = InMemoryFeedbackRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client, repo
    app.dependency_overrides.clear()


def test_sugerencia_anonima_se_persiste(
    client: tuple[TestClient, InMemoryFeedbackRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"message": "Añadid Spotify", "name": "Ana", "email": "ana@example.com"}
    respuesta = test_client.post("/feedback", json=cuerpo)

    assert respuesta.status_code == 204
    registros = repo.list_recent()
    assert len(registros) == 1
    assert registros[0].message == "Añadid Spotify"
    assert registros[0].kind == "suggestion"
    assert registros[0].user_id is None


def test_asocia_usuario_con_sesion(
    client: tuple[TestClient, InMemoryFeedbackRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"message": "Idea con sesión"}
    respuesta = test_client.post("/feedback", json=cuerpo, headers=auth_headers("user-7"))

    assert respuesta.status_code == 204
    assert repo.list_recent()[0].user_id == "user-7"


def test_contacto_como_kind(
    client: tuple[TestClient, InMemoryFeedbackRepository],
) -> None:
    test_client, repo = client
    cuerpo = {"message": "Consulta personal", "kind": "contact"}
    test_client.post("/feedback", json=cuerpo)
    assert repo.list_recent()[0].kind == "contact"


def test_mensaje_vacio_rechazado(
    client: tuple[TestClient, InMemoryFeedbackRepository],
) -> None:
    test_client, _ = client
    respuesta = test_client.post("/feedback", json={"message": ""})
    assert respuesta.status_code == 422


def test_correo_invalido_rechazado(
    client: tuple[TestClient, InMemoryFeedbackRepository],
) -> None:
    test_client, _ = client
    cuerpo = {"message": "hola", "email": "no-es-correo"}
    assert test_client.post("/feedback", json=cuerpo).status_code == 422


def _record() -> FeedbackRecord:
    return FeedbackRecord(kind="suggestion", message="x", created_at=datetime.now(UTC))


def test_notify_sin_smtp_no_envia(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "smtp_host", "")
    monkeypatch.setattr(settings, "feedback_to", "admin@example.com")
    assert mailer.notify_feedback(_record()) is False


def test_notify_con_smtp_envia(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_user", "bot@example.com")
    monkeypatch.setattr(settings, "smtp_password", SecretStr("secreto"))
    monkeypatch.setattr(settings, "feedback_to", "admin@example.com")
    monkeypatch.setattr(settings, "feedback_from", "bot@example.com")

    sent: dict[str, object] = {}

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            sent["host"] = host

        def __enter__(self) -> FakeSMTP:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def starttls(self) -> None:
            sent["tls"] = True

        def login(self, user: str, password: str) -> None:
            sent["login"] = user

        def send_message(self, message: object) -> None:
            sent["sent"] = True

    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    assert mailer.notify_feedback(_record()) is True
    assert sent["sent"] is True
    assert sent["tls"] is True


def test_notify_traga_errores_de_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "feedback_to", "admin@example.com")

    def boom(*args: object, **kwargs: object) -> object:
        raise OSError("sin red")

    monkeypatch.setattr(mailer.smtplib, "SMTP", boom)
    assert mailer.notify_feedback(_record()) is False
