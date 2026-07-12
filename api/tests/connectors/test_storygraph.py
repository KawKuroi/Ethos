"""Tests del conector de StoryGraph (import del export CSV)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ethos_api.connectors.storygraph.connector import (
    StorygraphConnector,
    StorygraphImportError,
    StorygraphRawData,
)
from ethos_api.schema import Category, ItemStatus

EXPORT = (
    "Title,Authors,Contributors,ISBN/UID,Format,Read Status,Date Added,"
    "Last Date Read,Read Count,Star Rating,Review,Tags,Owned?\n"
    "Piranesi,Susanna Clarke,,9781635575637,hardcover,read,2026/01/02,"
    "2026/02/10,1,4.5,Enorme.,fantasia,Yes\n"
    "Berserk,Kentaro Miura,,,paperback,currently-reading,2026/03/01,,0,,,,No\n"
    "Monster,Naoki Urasawa,,,paperback,to-read,2026/03/02,,0,,,,No\n"
    "Ulises,James Joyce,,,paperback,did-not-finish,2026/01/20,,0,,,,No\n"
)


def test_normaliza_el_export_al_contrato() -> None:
    items = StorygraphConnector().normalize(StorygraphRawData(csv_text=EXPORT))

    assert len(items) == 4
    piranesi = items[0]
    assert piranesi.category is Category.books
    assert piranesi.source == "storygraph"
    assert piranesi.status is ItemStatus.consumed
    assert piranesi.rating_normalized == 90  # 4.5 estrellas → 0-100
    assert piranesi.work.creators == ["Susanna Clarke"]
    assert piranesi.work.external_ids == {
        "storygraph": "9781635575637",
        "isbn13": "9781635575637",
    }
    assert piranesi.finished_at == datetime(2026, 2, 10, tzinfo=UTC)
    assert piranesi.review == "Enorme."
    assert piranesi.tags == ["fantasia"]

    berserk = items[1]
    assert berserk.status is ItemStatus.in_progress
    # Sin ISBN: external_id estable derivado del título y el autor.
    assert berserk.work.external_ids["storygraph"] == "berserk-kentaro-miura"

    assert items[2].status is ItemStatus.wishlist
    assert items[3].status is ItemStatus.abandoned


def test_csv_ajeno_lanza_error() -> None:
    with pytest.raises(StorygraphImportError):
        StorygraphConnector().normalize(
            StorygraphRawData(csv_text="Date,Name,Year\nx,y,z\n")
        )
