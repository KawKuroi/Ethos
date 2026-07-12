"""Cliente de la API v2 de MyAnimeList.

La lista pública de un usuario se lee con el client id de la app en el header
`X-MAL-CLIENT-ID`, sin OAuth (D62). Una lista privada o un usuario inexistente
responden 403/404. Acepta un `httpx.Client` inyectable y un throttle mínimo.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://api.myanimelist.net"
# Máximo por página de la API v2.
MAX_LIMIT = 1000
# Tope de páginas por refresco: cuida la cuota ante listas gigantes.
MAX_PAGES = 5

# Campos pedidos por lista (el resumen usa status, score y progreso).
_ANIME_FIELDS = "list_status,num_episodes,media_type"
_MANGA_FIELDS = "list_status,num_chapters,media_type"


class MalApiError(RuntimeError):
    """Error al consultar la API de MyAnimeList (lleva el código HTTP)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class MalClient:
    """Cliente mínimo de la API v2 de MyAnimeList."""

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
            headers={"X-MAL-CLIENT-ID": client_id},
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

    def get_anime_list(self, user_name: str) -> list[dict[str, Any]]:
        """Entradas de la lista de anime del usuario (todas las páginas)."""
        return self._get_list(f"/v2/users/{user_name}/animelist", _ANIME_FIELDS)

    def get_manga_list(self, user_name: str) -> list[dict[str, Any]]:
        """Entradas de la lista de manga del usuario (todas las páginas)."""
        return self._get_list(f"/v2/users/{user_name}/mangalist", _MANGA_FIELDS)

    def _get_list(self, path: str, fields: str) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        params: dict[str, str] = {
            "fields": fields,
            "limit": str(MAX_LIMIT),
            "nsfw": "true",
        }
        url: str | None = path
        for _ in range(MAX_PAGES):
            if url is None:
                break
            self._throttle()
            response = self._client.get(url, params=params if url == path else None)
            if response.status_code != 200:
                raise MalApiError(
                    f"MyAnimeList respondió {response.status_code}",
                    status_code=response.status_code,
                )
            body: Any = response.json()
            if not isinstance(body, dict):
                raise MalApiError("Respuesta inesperada de MyAnimeList")
            entries.extend(body.get("data", []))
            url = body.get("paging", {}).get("next")
        return entries
