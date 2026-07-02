"""Tests de normalización del conector de Steam (golden-file)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ethos_api.connectors.steam.connector import SteamConnector, SteamRawData
from ethos_api.schema import Category, IngestMode, ItemStatus

_FIXTURES = Path(__file__).parent.parent / "fixtures"


def _load(nombre: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / nombre).read_text(encoding="utf-8"))


def _raw() -> SteamRawData:
    return SteamRawData(
        owned_games=_load("steam_owned_games.json"),
        player_summary=_load("steam_player_summary.json"),
        recently_played=_load("steam_recently_played.json"),
    )


def test_identidad_del_conector() -> None:
    assert SteamConnector.id == "steam"
    assert SteamConnector.category is Category.games
    assert SteamConnector.ingest_mode is IngestMode.api


def test_normaliza_biblioteca() -> None:
    items = SteamConnector().normalize(_raw())
    assert len(items) == 2

    por_appid = {item.work.external_ids["steam_appid"]: item for item in items}

    tf2 = por_appid["440"]
    assert tf2.category is Category.games
    assert tf2.status is ItemStatus.in_library
    assert tf2.work.title == "Team Fortress 2"
    assert tf2.engagement["playtime_minutes"] == 1200
    assert tf2.engagement["playtime_2weeks_minutes"] == 90
    assert "last_played_at" in tf2.work.extra
    assert tf2.source == "steam"

    dota = por_appid["570"]
    assert dota.engagement["playtime_minutes"] == 5000
    assert "playtime_2weeks_minutes" not in dota.engagement


def test_extrae_perfil() -> None:
    profile = SteamConnector().profile(_raw())
    assert profile.steamid == "76561197960287930"
    assert profile.persona_name == "Jugador"
    assert profile.visibility == 3
