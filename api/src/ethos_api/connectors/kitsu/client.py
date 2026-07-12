"""Cliente de la API JSON:API de Kitsu.

La biblioteca de un usuario es pública por su slug/nombre: la lectura no
requiere key ni OAuth (D62). Dos pasos: resolver el id del usuario por su
nombre y pedir sus library entries con la obra incluida (`include=anime` o
`include=manga`). Acepta un `httpx.Client` inyectable y un throttle mínimo.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://kitsu.io/api/edge"
# Máximo por página que admite library-entries.
MAX_LIMIT = 500
# Tope de páginas por tipo (anime/manga) por refresco.
MAX_PAGES = 6


class KitsuApiError(RuntimeError):
    """Error al consultar la API de Kitsu (lleva el código HTTP si lo hubo)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class KitsuClient:
    """Cliente mínimo de la API de Kitsu."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 0.5,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or httpx.Client(
            base_url=_BASE_URL,
            timeout=15.0,
            headers={"Accept": "application/vnd.api+json"},
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

    def _get(self, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        self._throttle()
        response = self._client.get(url, params=params)
        if response.status_code != 200:
            raise KitsuApiError(
                f"Kitsu respondió {response.status_code}",
                status_code=response.status_code,
            )
        body: Any = response.json()
        if not isinstance(body, dict):
            raise KitsuApiError("Respuesta inesperada de Kitsu")
        return body

    def find_user_id(self, user_name: str) -> str:
        """Resuelve el id numérico del usuario por su nombre/slug."""
        body = self._get("/users", {"filter[name]": user_name, "page[limit]": "1"})
        data = body.get("data", [])
        if not data:
            raise KitsuApiError(
                f"No existe el usuario {user_name} en Kitsu", status_code=404
            )
        return str(data[0].get("id", ""))

    def get_library(self, user_id: str, kind: str) -> dict[str, Any]:
        """Library entries del usuario para `kind` (anime|manga), paginadas.

        Devuelve `{"data": [...entradas...], "included": [...obras...]}` con
        todas las páginas concatenadas.
        """
        entries: list[dict[str, Any]] = []
        included: list[dict[str, Any]] = []
        params: dict[str, str] = {
            "filter[userId]": user_id,
            "filter[kind]": kind,
            "include": kind,
            "page[limit]": str(MAX_LIMIT),
        }
        url: str | None = "/library-entries"
        for _ in range(MAX_PAGES):
            if url is None:
                break
            body = self._get(url, params if url == "/library-entries" else None)
            entries.extend(body.get("data", []))
            included.extend(body.get("included", []))
            url = body.get("links", {}).get("next")
        return {"data": entries, "included": included}
