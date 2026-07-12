"""Tests del cliente y el conector de Hardcover."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from ethos_api.connectors.hardcover.client import HardcoverApiError, HardcoverClient
from ethos_api.connectors.hardcover.connector import (
    HardcoverConnector,
    HardcoverRawData,
)
from ethos_api.schema import Category, ItemStatus

USER_BOOKS: list[dict[str, Any]] = [
    {
        "book_id": 101,
        "status_id": 3,
        "rating": 4.5,
        "review": "Enorme.",
        "date_added": "2026-01-02",
        "last_read_date": "2026-02-10",
        "book": {
            "title": "Piranesi",
            "pages": 272,
            "release_year": 2020,
            "contributions": [{"author": {"name": "Susanna Clarke"}}],
        },
    },
    {
        "book_id": 202,
        "status_id": 2,
        "rating": None,
        "book": {
            "title": "The Spear Cuts Through Water",
            "pages": 528,
            "contributions": [{"author": {"name": "Simon Jimenez"}}],
        },
    },
    {
        "book_id": 303,
        "status_id": 1,
        "book": {"title": "Tlön", "contributions": []},
    },
    {
        # Duplicado del primero: se ignora.
        "book_id": 101,
        "status_id": 3,
        "book": {"title": "Piranesi"},
    },
]


def _client(
    body: dict[str, Any], status_code: int = 200
) -> tuple[HardcoverClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status_code, json=body)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    return HardcoverClient(client=http), requests


def test_get_user_books_manda_el_bearer() -> None:
    client, requests = _client({"data": {"me": [{"user_books": USER_BOOKS}]}})
    books = client.get_user_books("token-123")
    assert len(books) == 4
    assert requests[0].headers["Authorization"] == "Bearer token-123"


def test_token_invalido_lanza_401() -> None:
    client, _ = _client({"errors": [{"message": "Could not verify JWT"}]})
    with pytest.raises(HardcoverApiError) as info:
        client.get_user_books("caducado")
    assert info.value.status_code == 401


def test_error_http_lanza_hardcover_error() -> None:
    client, _ = _client({}, status_code=500)
    with pytest.raises(HardcoverApiError):
        client.get_user_books("token")


def test_normaliza_user_books_al_contrato() -> None:
    items = HardcoverConnector().normalize(HardcoverRawData(user_books=USER_BOOKS))

    # Dedupe por book_id: 3 libros.
    assert len(items) == 3
    piranesi = items[0]
    assert piranesi.category is Category.books
    assert piranesi.source == "hardcover"
    assert piranesi.status is ItemStatus.consumed
    assert piranesi.rating_normalized == 90  # 4.5 estrellas → 0-100
    assert piranesi.work.creators == ["Susanna Clarke"]
    assert piranesi.work.year == 2020
    assert piranesi.work.external_ids == {"hardcover": "101"}
    assert piranesi.engagement == {"pages": 272, "read_count": 1}
    assert piranesi.review == "Enorme."
    assert piranesi.finished_at is not None

    leyendo = items[1]
    assert leyendo.status is ItemStatus.in_progress
    assert leyendo.rating_normalized is None

    wishlist = items[2]
    assert wishlist.status is ItemStatus.wishlist
