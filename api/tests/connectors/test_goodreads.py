"""Tests del conector de Goodreads (parseo del export CSV, D47)."""

from __future__ import annotations

import pytest

from ethos_api.connectors.goodreads.connector import (
    GoodreadsConnector,
    GoodreadsImportError,
    GoodreadsRawData,
)
from ethos_api.schema import Category, ItemStatus
from tests.books.helpers import GOODREADS_CSV


def _items() -> list:
    return GoodreadsConnector().normalize(GoodreadsRawData(csv_text=GOODREADS_CSV))


def test_normaliza_el_export_completo() -> None:
    items = _items()
    assert len(items) == 4
    assert all(i.category is Category.books for i in items)

    viento = next(i for i in items if i.work.title == "El nombre del viento")
    assert viento.status is ItemStatus.consumed
    assert viento.rating_normalized == 100
    assert viento.rating_original == "5"
    assert viento.work.creators == ["Patrick Rothfuss"]
    assert viento.engagement["pages"] == 662
    assert viento.finished_at is not None and viento.finished_at.year == 2026
    assert viento.review == "Una maravilla."
    # Goodreads exporta el ISBN como fórmula; debe quedar limpio.
    assert viento.work.external_ids["isbn13"] == "9780452286528"
    assert viento.work.external_ids["goodreads"] == "1"


def test_mapea_los_shelves_al_vocabulario_comun() -> None:
    items = {i.work.title: i for i in _items()}
    assert items["Project Hail Mary"].status is ItemStatus.in_progress
    assert items["La paciente silenciosa"].status is ItemStatus.wishlist
    assert items["Dune"].status is ItemStatus.consumed


def test_rating_cero_es_sin_puntuar() -> None:
    items = {i.work.title: i for i in _items()}
    assert items["Project Hail Mary"].rating_normalized is None
    assert items["Dune"].rating_normalized == 80


def test_csv_sin_columnas_de_goodreads_lanza_error() -> None:
    with pytest.raises(GoodreadsImportError):
        GoodreadsConnector().normalize(
            GoodreadsRawData(csv_text="foo,bar\n1,2\n")
        )


def test_filas_sin_titulo_se_descartan() -> None:
    csv_text = (
        "Book Id,Title,Author,Exclusive Shelf\n"
        "1,,Autor Fantasma,read\n"
        "2,Con título,Alguien,read\n"
    )
    items = GoodreadsConnector().normalize(GoodreadsRawData(csv_text=csv_text))
    assert [i.work.title for i in items] == ["Con título"]
