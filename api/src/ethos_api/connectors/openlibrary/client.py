"""Cliente de la API "My Books" de Open Library.

El reading log de un usuario se lee por su username sin key ni OAuth (D62),
siempre que el usuario lo tenga en público (Settings → Privacy). Tres estantes:
want-to-read, currently-reading y already-read. Un log privado responde
403/404. Acepta un `httpx.Client` inyectable y un throttle mínimo.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_BASE_URL = "https://openlibrary.org"
# Entradas por página del reading log.
PAGE_SIZE = 100
# Tope de páginas por estante por refresco.
MAX_PAGES = 10

SHELVES = ("want-to-read", "currently-reading", "already-read")


class OpenLibraryApiError(RuntimeError):
    """Error al consultar Open Library (lleva el código HTTP si lo hubo)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class OpenLibraryClient:
    """Cliente mínimo del reading log de Open Library."""

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

    def get_shelf(self, user_name: str, shelf: str) -> list[dict[str, Any]]:
        """Entradas del estante (`reading_log_entries`), todas las páginas."""
        entries: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            self._throttle()
            response = self._client.get(
                f"/people/{user_name}/books/{shelf}.json", params={"page": str(page)}
            )
            if response.status_code != 200:
                raise OpenLibraryApiError(
                    f"Open Library respondió {response.status_code} para {user_name}",
                    status_code=response.status_code,
                )
            body: Any = response.json()
            if not isinstance(body, dict):
                raise OpenLibraryApiError("Respuesta inesperada de Open Library")
            if "error" in body:
                # Un reading log privado responde 200 con un error embebido.
                raise OpenLibraryApiError(
                    str(body.get("error", "Reading log privado")), status_code=403
                )
            page_entries = body.get("reading_log_entries", [])
            entries.extend(page_entries)
            if len(page_entries) < PAGE_SIZE:
                break
        return entries
