"""Helpers del slice de juegos: fake del cliente de Steam sobre fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ethos_api.connectors.steam.client import SteamApiError

_FIXTURES = Path(__file__).parent.parent / "fixtures"


def load_fixture(nombre: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / nombre).read_text(encoding="utf-8"))


class FakeSteamApi:
    """Cliente falso de Steam alimentado por las fixtures de la suite."""

    def __init__(
        self,
        *,
        visibility: int = 3,
        fail_owned: bool = False,
        fail_achievements: bool = False,
    ) -> None:
        self.visibility = visibility
        self.fail_owned = fail_owned
        self.fail_achievements = fail_achievements
        self.achievement_calls: list[int] = []

    def get_owned_games(self, steamid: str) -> dict[str, Any]:
        if self.fail_owned:
            raise SteamApiError("Steam respondió 500 en owned games")
        if self.visibility != 3:
            return {"response": {}}
        return load_fixture("steam_owned_games.json")

    def get_recently_played(self, steamid: str) -> dict[str, Any]:
        return load_fixture("steam_recently_played.json")

    def get_player_summary(self, steamid: str) -> dict[str, Any]:
        payload = load_fixture("steam_player_summary.json")
        payload["response"]["players"][0]["communityvisibilitystate"] = self.visibility
        return payload

    def get_wishlist(self, steamid: str) -> dict[str, Any]:
        return load_fixture("steam_wishlist.json")

    def get_player_achievements(self, steamid: str, appid: int) -> dict[str, Any]:
        self.achievement_calls.append(appid)
        if self.fail_achievements:
            raise SteamApiError("juego sin logros")
        return load_fixture("steam_achievements.json")
