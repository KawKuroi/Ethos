"""Tests del conector de Spotify (import de historial)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from ethos_api.connectors.spotify.connector import (
    SpotifyConnector,
    SpotifyImportError,
    SpotifyRawData,
)
from ethos_api.schema import Category

EXTENDED = [
    {
        "ts": "2026-03-01T18:22:05Z",
        "ms_played": 215000,
        "master_metadata_track_name": "Belinda Says",
        "master_metadata_album_artist_name": "Alvvays",
        "master_metadata_album_album_name": "Blue Rev",
    },
    {
        # Menos de 30 s: no cuenta como escucha.
        "ts": "2026-03-01T18:23:00Z",
        "ms_played": 8000,
        "master_metadata_track_name": "Skip",
        "master_metadata_album_artist_name": "Alguien",
    },
    {
        # Podcast u obra sin metadatos de track: se descarta.
        "ts": "2026-03-01T18:24:00Z",
        "ms_played": 90000,
        "master_metadata_track_name": None,
        "master_metadata_album_artist_name": None,
    },
]

SIMPLE = [
    {
        "endTime": "2026-03-01 18:22",
        "artistName": "Alvvays",
        "trackName": "Archie, Marry Me",
        "msPlayed": 200000,
    }
]


def test_normaliza_el_formato_ampliado() -> None:
    events = SpotifyConnector().normalize(SpotifyRawData(json_text=json.dumps(EXTENDED)))
    assert len(events) == 1
    evento = events[0]
    assert evento.category is Category.music
    assert evento.source == "spotify"
    assert evento.payload == {
        "artist": "Alvvays",
        "track": "Belinda Says",
        "release": "Blue Rev",
    }
    assert evento.occurred_at == datetime(2026, 3, 1, 18, 22, 5, tzinfo=UTC)


def test_normaliza_el_formato_simple() -> None:
    events = SpotifyConnector().normalize(SpotifyRawData(json_text=json.dumps(SIMPLE)))
    assert len(events) == 1
    assert events[0].payload["track"] == "Archie, Marry Me"
    assert events[0].occurred_at == datetime(2026, 3, 1, 18, 22, tzinfo=UTC)


def test_json_invalido_lanza_error() -> None:
    with pytest.raises(SpotifyImportError):
        SpotifyConnector().normalize(SpotifyRawData(json_text="no es json"))


def test_json_ajeno_lanza_error() -> None:
    with pytest.raises(SpotifyImportError):
        SpotifyConnector().normalize(SpotifyRawData(json_text='[{"otro": 1}]'))
