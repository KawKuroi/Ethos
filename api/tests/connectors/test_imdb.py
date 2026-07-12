"""Tests del conector de IMDb (import del CSV de ratings)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ethos_api.connectors.imdb.connector import (
    ImdbConnector,
    ImdbImportError,
    ImdbRawData,
)
from ethos_api.schema import Category, ItemStatus

RATINGS = (
    "Const,Your Rating,Date Rated,Title,Title Type,IMDb Rating,Runtime (mins),"
    "Year,Genres,Num Votes,Release Date,Directors\n"
    "tt0111161,10,2026-01-05,The Shawshank Redemption,Movie,9.3,142,1994,"
    "Drama,3000000,1994-09-23,Frank Darabont\n"
    "tt0903747,9,2026-02-10,Breaking Bad,TV Series,9.5,45,2008,"
    '"Crime, Drama, Thriller",2400000,2008-01-20,\n'
    "tt0111161,10,2026-01-05,The Shawshank Redemption,Movie,9.3,142,1994,"
    "Drama,3000000,1994-09-23,Frank Darabont\n"
)


def test_normaliza_ratings_al_contrato() -> None:
    items = ImdbConnector().normalize(ImdbRawData(csv_text=RATINGS))

    # El duplicado por Const se ignora: 2 obras.
    assert len(items) == 2
    pelicula = items[0]
    assert pelicula.category is Category.film
    assert pelicula.source == "imdb"
    assert pelicula.status is ItemStatus.consumed
    assert pelicula.rating_normalized == 100  # 10 → 0-100
    assert pelicula.work.external_ids == {"imdb": "tt0111161"}
    assert pelicula.work.extra["media_type"] == "movie"
    assert pelicula.finished_at == datetime(2026, 1, 5, tzinfo=UTC)
    assert pelicula.tags == ["Drama"]

    serie = items[1]
    assert serie.work.extra["media_type"] == "show"
    assert serie.tags == ["Crime", "Drama", "Thriller"]


def test_csv_ajeno_lanza_error() -> None:
    with pytest.raises(ImdbImportError):
        ImdbConnector().normalize(ImdbRawData(csv_text="Title,Author\nx,y\n"))
