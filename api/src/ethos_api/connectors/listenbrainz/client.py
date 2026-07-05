"""Cliente de la API de ListenBrainz.

Los listens de un usuario son públicos por su username: la lectura no requiere
token (D37). Acepta un `httpx.Client` inyectable para testear sin red y un
throttle mínimo entre llamadas para no abusar del servicio.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://api.listenbrainz.org"
# Máximo por página que admite la API de listens.
MAX_COUNT = 100


class ListenBrainzApiError(RuntimeError):
    """Error al consultar la API de ListenBrainz."""


class ListenBrainzClient:
    """Cliente mínimo de la API de ListenBrainz."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 0.5,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
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

    def get_listens(
        self, user_name: str, *, min_ts: int | None = None, count: int = MAX_COUNT
    ) -> dict[str, Any]:
        """Listens del usuario, del más reciente al más antiguo.

        `min_ts` (epoch en segundos) trae solo listens posteriores, para el
        refresco incremental (D40).
        """
        self._throttle()
        params: dict[str, str] = {"count": str(min(count, MAX_COUNT))}
        if min_ts is not None:
            params["min_ts"] = str(min_ts)
        response = self._client.get(f"/1/user/{user_name}/listens", params=params)
        if response.status_code != 200:
            raise ListenBrainzApiError(
                f"ListenBrainz respondió {response.status_code} para {user_name}"
            )
        data: Any = response.json()
        if not isinstance(data, dict):
            raise ListenBrainzApiError("Respuesta inesperada de ListenBrainz")
        return data
