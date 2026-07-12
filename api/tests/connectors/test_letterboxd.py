"""Tests del conector de Letterboxd (import de diary/watched/ratings)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ethos_api.connectors.letterboxd.connector import (
    LetterboxdConnector,
    LetterboxdImportError,
    LetterboxdRawData,
)
from ethos_api.schema import Category, ItemStatus

DIARY = (
    "Date,Name,Year,Letterboxd URI,Rating,Rewatch,Tags,Watched Date\n"
    "2026-03-01,Paddington 2,2017,https://boxd.it/abc1,5,,cozy,2026-02-28\n"
    "2026-03-05,Paddington 2,2017,https://boxd.it/abc1,5,Yes,,2026-03-04\n"
    "2026-01-10,Aftersun,2022,https://boxd.it/def2,4.5,,,2026-01-09\n"
)

WATCHED = (
    "Date,Name,Year,Letterboxd URI\n"
    "2026-02-01,La Ciénaga,2001,https://boxd.it/ggg3\n"
)


def test_normaliza_el_diario_y_agrupa_rewatches() -> None:
    items = LetterboxdConnector().normalize(LetterboxdRawData(csv_text=DIARY))

    assert len(items) == 2
    paddington = next(i for i in items if i.work.title == "Paddington 2")
    assert paddington.category is Category.film
    assert paddington.source == "letterboxd"
    assert paddington.status is ItemStatus.consumed
    assert paddington.rating_normalized == 100  # 5 estrellas → 0-100
    # Dos filas del diario (la segunda rewatch): 1 + 2 reproducciones.
    assert paddington.engagement["plays"] == 3
    assert paddington.finished_at == datetime(2026, 3, 4, tzinfo=UTC)
    assert paddington.work.external_ids == {"letterboxd": "abc1"}
    assert paddington.work.extra["media_type"] == "movie"
    assert paddington.work.extra["last_watched_at"] == "2026-03-04T00:00:00+00:00"

    aftersun = next(i for i in items if i.work.title == "Aftersun")
    assert aftersun.rating_normalized == 90


def test_normaliza_watched_sin_rating() -> None:
    items = LetterboxdConnector().normalize(LetterboxdRawData(csv_text=WATCHED))
    assert len(items) == 1
    assert items[0].rating_normalized is None
    assert items[0].engagement["plays"] == 1


def test_csv_ajeno_lanza_error() -> None:
    with pytest.raises(LetterboxdImportError):
        LetterboxdConnector().normalize(
            LetterboxdRawData(csv_text="Title,Author\nx,y\n")
        )
