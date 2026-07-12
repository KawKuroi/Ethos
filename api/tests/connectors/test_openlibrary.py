"""Tests del cliente y el conector de Open Library."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ethos_api.connectors.openlibrary.client import (
    OpenLibraryApiError,
    OpenLibraryClient,
)
from ethos_api.connectors.openlibrary.connector import (
    OpenLibraryConnector,
    OpenLibraryRawData,
)
from ethos_api.schema import Category, ItemStatus


def _entry(title: str, key: str, **extra: Any) -> dict[str, Any]:
    work = {"title": title, "key": key, "author_names": ["Ursula K. Le Guin"]}
    work.update(extra)
    return {"work": work, "logged_date": "2026/03/23, 15:31:35"}


SHELVES: dict[str, list[dict[str, Any]]] = {
    "already-read": [
        _entry("The Dispossessed", "/works/OL45804W", first_publish_year=1974),
        # Duplicado del mismo work en otro estante: gana el primero.
    ],
    "currently-reading": [_entry("The Left Hand of Darkness", "/works/OL45883W")],
    "want-to-read": [
        _entry("The Dispossessed", "/works/OL45804W"),
        _entry("A Wizard of Earthsea", "/works/OL45900W"),
    ],
}


def _client(
    respuestas: list[dict[str, Any]], status_code: int = 200
) -> tuple[OpenLibraryClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []
    paginas = iter(respuestas)

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if status_code != 200:
            return httpx.Response(status_code, json={})
        return httpx.Response(200, json=next(paginas))

    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://openlibrary.org"
    )
    return OpenLibraryClient(client=http), requests


def test_get_shelf_lee_las_entradas() -> None:
    client, requests = _client(
        [{"page": 1, "reading_log_entries": SHELVES["already-read"]}]
    )
    entries = client.get_shelf("lectora", "already-read")
    assert len(entries) == 1
    assert "/people/lectora/books/already-read.json" in requests[0].url.path


def test_log_privado_lanza_403() -> None:
    client, _ = _client([{"error": "This reading log is private"}])
    with pytest.raises(OpenLibraryApiError) as info:
        client.get_shelf("privada", "already-read")
    assert info.value.status_code == 403


def test_usuario_inexistente_propaga_el_codigo() -> None:
    client, _ = _client([], status_code=404)
    with pytest.raises(OpenLibraryApiError) as info:
        client.get_shelf("nadie", "already-read")
    assert info.value.status_code == 404


def test_normaliza_reading_log_al_contrato() -> None:
    items = OpenLibraryConnector().normalize(OpenLibraryRawData(shelves=SHELVES))

    # El work repetido entre estantes se cuenta una vez: 3 obras.
    assert len(items) == 3
    leido = items[0]
    assert leido.category is Category.books
    assert leido.source == "openlibrary"
    assert leido.status is ItemStatus.consumed
    assert leido.work.title == "The Dispossessed"
    assert leido.work.creators == ["Ursula K. Le Guin"]
    assert leido.work.year == 1974
    assert leido.work.external_ids == {"openlibrary": "OL45804W"}
    assert leido.finished_at is not None
    assert leido.engagement["read_count"] == 1

    leyendo = items[1]
    assert leyendo.status is ItemStatus.in_progress
    assert leyendo.finished_at is None
