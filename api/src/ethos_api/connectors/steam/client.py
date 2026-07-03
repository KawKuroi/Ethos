"""Cliente de la Steam Web API.

Acepta un `httpx.Client` inyectable para poder testear sin red. La API key es
del servidor y nunca se expone al cliente final. Un throttle de intervalo
mínimo entre llamadas cuida la cuota de la key (100k/día) y evita que un
abuso interno (p. ej. el cálculo de completado, una llamada por juego) la
queme o la haga banear.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://api.steampowered.com"


class SteamApiError(RuntimeError):
    """Error al consultar la Steam Web API."""


class SteamApiClient:
    """Cliente mínimo de la Steam Web API."""

    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._api_key = api_key
        self._client = client or httpx.Client(base_url=_BASE_URL, timeout=15.0)
        self._min_interval = min_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_call = float("-inf")

    def _throttle(self) -> None:
        # Espera lo que falte para respetar el intervalo mínimo entre llamadas.
        wait = self._min_interval - (self._clock() - self._last_call)
        if wait > 0:
            self._sleep(wait)
        self._last_call = self._clock()

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        self._throttle()
        # El crudo de Steam es JSON sin tipar; se devuelve como dict y la capa de
        # normalización lo convierte al contrato tipado.
        respuesta = self._client.get(path, params={"key": self._api_key, **params})
        if respuesta.status_code != 200:
            raise SteamApiError(f"Steam respondió {respuesta.status_code} en {path}")
        data: Any = respuesta.json()
        if not isinstance(data, dict):
            raise SteamApiError(f"Respuesta inesperada de Steam en {path}")
        return data

    def get_owned_games(self, steamid: str) -> dict[str, Any]:
        """Biblioteca con horas totales y última sesión."""
        return self._get(
            "/IPlayerService/GetOwnedGames/v1/",
            {"steamid": steamid, "include_appinfo": "1", "format": "json"},
        )

    def get_recently_played(self, steamid: str) -> dict[str, Any]:
        """Juegos jugados en las últimas dos semanas."""
        return self._get(
            "/IPlayerService/GetRecentlyPlayedGames/v1/",
            {"steamid": steamid, "format": "json"},
        )

    def get_player_summary(self, steamid: str) -> dict[str, Any]:
        """Datos públicos del perfil (nombre, avatar, visibilidad)."""
        return self._get(
            "/ISteamUser/GetPlayerSummaries/v2/",
            {"steamids": steamid, "format": "json"},
        )

    def get_wishlist(self, steamid: str) -> dict[str, Any]:
        """Deseados del usuario (appid, prioridad y fecha; sin títulos, D32)."""
        return self._get(
            "/IWishlistService/GetWishlist/v1/",
            {"steamid": steamid, "format": "json"},
        )

    def get_player_achievements(self, steamid: str, appid: int) -> dict[str, Any]:
        """Logros del usuario en un juego (una llamada por juego, D33).

        Un perfil privado o un juego sin logros responden distinto de 200;
        el llamador decide cómo degradar, aquí solo viaja el crudo.
        """
        return self._get(
            "/ISteamUserStats/GetPlayerAchievements/v1/",
            {"steamid": steamid, "appid": str(appid), "format": "json"},
        )
