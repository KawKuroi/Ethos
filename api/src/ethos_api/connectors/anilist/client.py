"""Cliente de la API GraphQL de AniList.

Las listas de anime y manga de un usuario son públicas por su username; leerlas
no requiere key ni OAuth (D45). Una sola consulta trae ambas colecciones.
Acepta un `httpx.Client` inyectable para testear sin red y un throttle mínimo
entre llamadas para cuidar la cuota de la API (90 req/min).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_GRAPHQL_URL = "https://graphql.anilist.co"

# Colecciones de anime y manga del usuario en una sola consulta. El score se
# pide normalizado a 0-100 (POINT_100) sin importar el formato del usuario.
_MEDIA_LISTS_QUERY = """
query ($userName: String) {
  anime: MediaListCollection(userName: $userName, type: ANIME) {
    lists {
      isCustomList
      entries {
        status
        score(format: POINT_100)
        progress
        repeat
        updatedAt
        media { id title { romaji english } episodes format }
      }
    }
  }
  manga: MediaListCollection(userName: $userName, type: MANGA) {
    lists {
      isCustomList
      entries {
        status
        score(format: POINT_100)
        progress
        repeat
        updatedAt
        media { id title { romaji english } chapters format }
      }
    }
  }
}
"""


class AniListApiError(RuntimeError):
    """Error al consultar la API de AniList (lleva el código HTTP si lo hubo)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AniListApiClient:
    """Cliente mínimo de la API GraphQL de AniList."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 0.7,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or httpx.Client(
            base_url=_GRAPHQL_URL,
            timeout=15.0,
            headers={"Content-Type": "application/json"},
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

    def get_media_lists(self, user_name: str) -> dict[str, Any]:
        """Colecciones de anime y manga del usuario (claves `anime` y `manga`)."""
        self._throttle()
        response = self._client.post(
            "",
            json={"query": _MEDIA_LISTS_QUERY, "variables": {"userName": user_name}},
        )
        if response.status_code != 200:
            raise AniListApiError(
                f"AniList respondió {response.status_code}",
                status_code=response.status_code,
            )
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("data"), dict):
            raise AniListApiError("Respuesta inesperada de AniList")
        # GraphQL puede devolver 200 con errores embebidos (p. ej. usuario
        # privado); se propaga el status del primer error.
        errors = body.get("errors")
        if errors and isinstance(errors, list):
            first = errors[0] if isinstance(errors[0], dict) else {}
            raise AniListApiError(
                str(first.get("message", "Error de AniList")),
                status_code=first.get("status"),
            )
        return body["data"]
