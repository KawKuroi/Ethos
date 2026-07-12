"""Cliente de la API de Last.fm.

Los scrobbles de un usuario son públicos por su username: leerlos solo
requiere la API key de la app (config `LASTFM_API_KEY`), sin OAuth (D62).
Acepta un `httpx.Client` inyectable para testear sin red y un throttle mínimo
entre llamadas para cuidar la cuota de la key.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://ws.audioscrobbler.com"
# Máximo por página que admite user.getRecentTracks.
MAX_LIMIT = 200


class LastfmApiError(RuntimeError):
    """Error al consultar la API de Last.fm (lleva el código si lo hubo)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LastfmClient:
    """Cliente mínimo de la API de Last.fm."""

    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 0.3,
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
        wait = self._min_interval - (self._clock() - self._last_call)
        if wait > 0:
            self._sleep(wait)
        self._last_call = self._clock()

    def get_recent_tracks(
        self,
        user_name: str,
        *,
        from_ts: int | None = None,
        page: int = 1,
        limit: int = MAX_LIMIT,
    ) -> dict[str, Any]:
        """Scrobbles del usuario, del más reciente al más antiguo.

        `from_ts` (epoch en segundos) trae solo scrobbles posteriores, para el
        refresco incremental (como el `min_ts` de ListenBrainz, D40).
        """
        self._throttle()
        params: dict[str, str] = {
            "method": "user.getrecenttracks",
            "user": user_name,
            "api_key": self._api_key,
            "format": "json",
            "limit": str(min(limit, MAX_LIMIT)),
            "page": str(page),
        }
        if from_ts is not None:
            params["from"] = str(from_ts)
        response = self._client.get("/2.0/", params=params)
        if response.status_code != 200:
            raise LastfmApiError(
                f"Last.fm respondió {response.status_code} para {user_name}",
                status_code=response.status_code,
            )
        data: Any = response.json()
        if not isinstance(data, dict):
            raise LastfmApiError("Respuesta inesperada de Last.fm")
        # La API devuelve errores como 200 con {"error": n, "message": "..."}.
        if "error" in data:
            code = data.get("error")
            # 6 = usuario no encontrado; 17 = perfil privado.
            status = 404 if code == 6 else 403 if code == 17 else None
            raise LastfmApiError(
                str(data.get("message", "Error de Last.fm")), status_code=status
            )
        return data
