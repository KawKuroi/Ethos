"""Tests del generador de resumen y del contexto descargable (D33/D34)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.connectors.steam.connector import SteamConnector, SteamRawData
from ethos_api.games.context import build_games_context
from ethos_api.games.summary import build_games_summary
from tests.games.helpers import load_fixture


def _items_y_perfil() -> tuple[list, object]:
    raw = SteamRawData(
        owned_games=load_fixture("steam_owned_games.json"),
        player_summary=load_fixture("steam_player_summary.json"),
        recently_played=load_fixture("steam_recently_played.json"),
        wishlist=load_fixture("steam_wishlist.json"),
        completion_by_appid={440: 75.0},
        genres_by_appid={440: ["Acción", "Multijugador"], 570: ["Acción", "MOBA"]},
    )
    connector = SteamConnector()
    return connector.normalize(raw), connector.profile(raw)


def test_resumen_agrega_biblioteca_y_wishlist() -> None:
    items, profile = _items_y_perfil()
    synced = datetime(2026, 7, 3, tzinfo=UTC)
    summary = build_games_summary(items, profile, synced_at=synced)  # type: ignore[arg-type]

    assert summary.games == 2
    assert summary.wishlisted == 3
    # 1200 + 5000 minutos = 103.3 horas.
    assert summary.hours == 103.3
    assert summary.avg_completion_pct == 75.0
    assert summary.persona_name == "Jugador"
    assert summary.last_synced_at == synced

    # Top ordenado por horas: Dota (5000 min) primero.
    assert summary.top_by_hours[0].title == "Dota 2"
    assert summary.top_by_hours[1].title == "Team Fortress 2"
    assert summary.top_by_hours[1].completion_pct == 75.0

    # Reciente: solo TF2 tiene actividad en dos semanas.
    assert [r.title for r in summary.recently_played] == ["Team Fortress 2"]

    # Géneros: el top los lleva y el agregado cuenta juegos por género (D55).
    assert summary.top_by_hours[0].genres == ["Acción", "MOBA"]
    assert summary.top_genres[0].name == "Acción"
    assert summary.top_genres[0].games == 2


def test_contexto_tiene_la_forma_d34() -> None:
    items, profile = _items_y_perfil()
    summary = build_games_summary(items, profile)  # type: ignore[arg-type]
    context = build_games_context(summary, items, profile)  # type: ignore[arg-type]

    assert context["namespace"] == "games.*"
    assert context["provider"] == "steam"
    assert set(context) == {
        "namespace",
        "provider",
        "generated_at",
        "profile",
        "summary",
        "top_by_hours",
        "recently_played",
        "top_genres",
        "wishlist",
        "history",
    }
    resumen = context["summary"]
    assert isinstance(resumen, dict)
    assert resumen["games"] == 2
    wishlist = context["wishlist"]
    assert isinstance(wishlist, dict)
    assert wishlist["count"] == 3
    # Ordenada por prioridad ascendente (0 primero).
    assert wishlist["top_priority_appids"] == ["2379780", "1145360", "1030300"]
    # Historial (D60): biblioteca completa sin la wishlist (sin títulos, D32).
    history = context["history"]
    assert isinstance(history, dict)
    assert history["total"] == 2
    assert history["truncated"] is False
    titles = {e["title"] for e in history["entries"]}
    assert titles == {"Team Fortress 2", "Dota 2"}
