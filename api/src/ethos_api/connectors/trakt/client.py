"""Cliente de la API de Trakt.

Los datos "vistos" de un usuario son públicos por su username; leerlos solo
requiere el `client_id` de la app en el header `trakt-api-key` (sin OAuth, D41).
Acepta un `httpx.Client` inyectable para testear sin red y un throttle mínimo
entre llamadas para cuidar la cuota de la API.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://api.trakt.tv"
_API_VERSION = "2"


class TraktApiError(RuntimeError):
    """Error al consultar la API de Trakt (lleva el código HTTP si lo hubo)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class TraktApiClient:
    """Cliente mínimo de la API de Trakt."""

    def __init__(
        self,
        client_id: str,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 0.5,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or httpx.Client(
            base_url=_BASE_URL,
            timeout=15.0,
            headers={
                "trakt-api-key": client_id,
                "trakt-api-version": _API_VERSION,
                "Content-Type": "application/json",
            },
        )
        self._min_interval = min_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_call = float("-inf")

    def _throttle(self) -> None:
        wait = self._min_interval - (self._clock() - self._last_call)
        if wait > 0:
            self._sleep(wait)
        self._last_call = self._clock()

    def _get(self, path: str) -> Any:
        self._throttle()
        response = self._client.get(path)
        if response.status_code != 200:
            raise TraktApiError(
                f"Trakt respondió {response.status_code} en {path}",
                status_code=response.status_code,
            )
        return response.json()

    def get_user_stats(self, user_name: str) -> dict[str, Any]:
        """Estadísticas agregadas del usuario (minutos y conteos totales)."""
        data = self._get(f"/users/{user_name}/stats")
        if not isinstance(data, dict):
            raise TraktApiError("Respuesta inesperada de Trakt en /stats")
        return data

    def get_watched_movies(self, user_name: str) -> list[dict[str, Any]]:
        """Películas vistas por el usuario, con plays y última vez visto."""
        data = self._get(f"/users/{user_name}/watched/movies")
        if not isinstance(data, list):
            raise TraktApiError("Respuesta inesperada de Trakt en watched/movies")
        return data

    def get_watched_shows(self, user_name: str) -> list[dict[str, Any]]:
        """Series vistas por el usuario, con episodios vistos por temporada."""
        data = self._get(f"/users/{user_name}/watched/shows")
        if not isinstance(data, list):
            raise TraktApiError("Respuesta inesperada de Trakt en watched/shows")
        return data
