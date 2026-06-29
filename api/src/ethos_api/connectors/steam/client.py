"""Cliente de la Steam Web API.

Acepta un `httpx.Client` inyectable para poder testear sin red. La API key es
del servidor y nunca se expone al cliente final.
"""

from __future__ import annotations

from typing import Any

import httpx

_BASE_URL = "https://api.steampowered.com"


class SteamApiError(RuntimeError):
    """Error al consultar la Steam Web API."""


class SteamApiClient:
    """Cliente mínimo de la Steam Web API."""

    def __init__(self, api_key: str, *, client: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._client = client or httpx.Client(base_url=_BASE_URL, timeout=15.0)

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
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
