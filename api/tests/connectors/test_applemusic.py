"""Tests del conector de Apple Music (import del Play History Daily Tracks)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ethos_api.connectors.applemusic.connector import (
    AppleMusicConnector,
    AppleMusicImportError,
    AppleMusicRawData,
)
from ethos_api.schema import Category


def test_normaliza_el_play_history_diario() -> None:
    text = (
        "Track Description,Date Played,Play Duration Milliseconds,Play Count\n"
        "Alvvays - Belinda Says,20260301,215000,3\n"
        "Sin Separador,20260301,90000,1\n"
        "Alguien - Sin Fecha,,90000,1\n"
    )
    events = AppleMusicConnector().normalize(AppleMusicRawData(csv_text=text))
    # La fila sin "Artista - Pista" y la fila sin fecha se descartan.
    assert len(events) == 1
    evento = events[0]
    assert evento.category is Category.music
    assert evento.source == "applemusic"
    assert evento.payload == {"artist": "Alvvays", "track": "Belinda Says", "plays": "3"}
    assert evento.occurred_at == datetime(2026, 3, 1, tzinfo=UTC)


def test_columnas_ajenas_lanzan_error() -> None:
    with pytest.raises(AppleMusicImportError):
        AppleMusicConnector().normalize(
            AppleMusicRawData(csv_text="Title,Author\nx,y\n")
        )
