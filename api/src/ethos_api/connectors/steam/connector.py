"""Conector de Steam: identidad y normalización al contrato común."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work


@dataclass
class SteamRawData:
    """Respuestas crudas de la Steam Web API para un usuario."""

    owned_games: dict[str, Any]
    player_summary: dict[str, Any]
    recently_played: dict[str, Any] = field(default_factory=dict)
    wishlist: dict[str, Any] = field(default_factory=dict)
    # Completado por appid (0-100), calculado aparte con presupuesto (D33).
    completion_by_appid: dict[int, float] = field(default_factory=dict)


@dataclass
class SteamProfile:
    """Perfil normalizado de Steam (datos de `GetPlayerSummaries`)."""

    steamid: str
    persona_name: str
    avatar_url: str | None
    # communityvisibilitystate: 1 = privado, 3 = público.
    visibility: int | None


class SteamConnector(Connector[SteamRawData, NormalizedItem]):
    """Conector del proveedor Steam."""

    id: ClassVar[str] = "steam"
    category: ClassVar[Category] = Category.games
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "engagement", "external_ids"}
    )

    def normalize(self, raw: SteamRawData) -> list[NormalizedItem]:
        recent_2weeks = self._recent_playtime_by_appid(raw.recently_played)
        games = raw.owned_games.get("response", {}).get("games", [])
        items = [
            self._normalize_game(game, recent_2weeks, raw.completion_by_appid)
            for game in games
        ]
        items.extend(self._normalize_wishlist(raw.wishlist))
        return items

    def profile(self, raw: SteamRawData) -> SteamProfile:
        """Extrae el perfil del usuario desde `GetPlayerSummaries`."""
        players = raw.player_summary.get("response", {}).get("players", [])
        if not players:
            raise ValueError("La respuesta de perfil de Steam no trae jugadores")
        player = players[0]
        return SteamProfile(
            steamid=str(player["steamid"]),
            persona_name=str(player.get("personaname", "")),
            avatar_url=player.get("avatarfull"),
            visibility=player.get("communityvisibilitystate"),
        )

    def _normalize_game(
        self,
        game: dict[str, Any],
        recent_2weeks: dict[int, int],
        completion_by_appid: dict[int, float],
    ) -> NormalizedItem:
        appid = int(game["appid"])

        engagement: dict[str, int] = {
            "playtime_minutes": int(game.get("playtime_forever", 0)),
        }
        two_weeks = recent_2weeks.get(appid, int(game.get("playtime_2weeks", 0)))
        if two_weeks:
            engagement["playtime_2weeks_minutes"] = two_weeks

        extra: dict[str, object] = {}
        last_played = int(game.get("rtime_last_played", 0))
        if last_played:
            extra["last_played_at"] = datetime.fromtimestamp(
                last_played, tz=UTC
            ).isoformat()
        completion = completion_by_appid.get(appid)
        if completion is not None:
            extra["completion_pct"] = round(completion, 1)

        work = Work(
            title=str(game.get("name", "")),
            external_ids={"steam_appid": str(appid)},
            extra=extra,
        )
        return NormalizedItem(
            work=work,
            category=Category.games,
            status=ItemStatus.in_library,
            engagement=engagement,
            source=self.id,
            provenance={"title": self.id, "engagement": self.id},
        )

    def _normalize_wishlist(self, wishlist: dict[str, Any]) -> list[NormalizedItem]:
        """Deseados como items `wishlist` (sin título en v1, D32)."""
        entries = wishlist.get("response", {}).get("items", [])
        items: list[NormalizedItem] = []
        for entry in entries:
            appid = int(entry["appid"])
            extra: dict[str, object] = {}
            priority = entry.get("priority")
            if priority is not None:
                extra["wishlist_priority"] = int(priority)
            added_at = None
            date_added = int(entry.get("date_added", 0))
            if date_added:
                added_at = datetime.fromtimestamp(date_added, tz=UTC)
            work = Work(
                title="",
                external_ids={"steam_appid": str(appid)},
                extra=extra,
            )
            items.append(
                NormalizedItem(
                    work=work,
                    category=Category.games,
                    status=ItemStatus.wishlist,
                    added_at=added_at,
                    source=self.id,
                    provenance={"status": self.id},
                )
            )
        return items

    @staticmethod
    def completion_from_achievements(payload: dict[str, Any]) -> float | None:
        """Porcentaje de logros conseguidos desde `GetPlayerAchievements`."""
        stats = payload.get("playerstats", {})
        achievements = stats.get("achievements")
        if not achievements:
            return None
        achieved = sum(1 for a in achievements if a.get("achieved"))
        return achieved * 100.0 / len(achievements)

    @staticmethod
    def _recent_playtime_by_appid(recently_played: dict[str, Any]) -> dict[int, int]:
        games = recently_played.get("response", {}).get("games", [])
        return {int(g["appid"]): int(g.get("playtime_2weeks", 0)) for g in games}
