"""Cliente de la API GraphQL de Hardcover.

El usuario genera su token en hardcover.app (Settings → Hardcover API; expira
cada año) y Ethos lo guarda cifrado como credencial (D20/D62). La API se
consulta con `Authorization: Bearer <token>`; el token identifica al usuario,
así que `me { user_books }` trae su biblioteca. Rate limit: 60 req/min.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

_GRAPHQL_URL = "https://api.hardcover.app/v1/graphql"

# Biblioteca completa del usuario autenticado por el token.
_USER_BOOKS_QUERY = """
query {
  me {
    user_books {
      book_id
      status_id
      rating
      review
      date_added
      last_read_date
      book {
        title
        pages
        release_year
        contributions { author { name } }
      }
    }
  }
}
"""


class HardcoverApiError(RuntimeError):
    """Error al consultar la API de Hardcover (lleva el código HTTP)."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class HardcoverClient:
    """Cliente mínimo de la API GraphQL de Hardcover."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        min_interval_seconds: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or httpx.Client(timeout=20.0)
        self._min_interval = min_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_call = float("-inf")

    def _throttle(self) -> None:
        wait = self._min_interval - (self._clock() - self._last_call)
        if wait > 0:
            self._sleep(wait)
        self._last_call = self._clock()

    def get_user_books(self, token: str) -> list[dict[str, Any]]:
        """`user_books` del usuario dueño del token."""
        self._throttle()
        response = self._client.post(
            _GRAPHQL_URL,
            json={"query": _USER_BOOKS_QUERY},
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code != 200:
            raise HardcoverApiError(
                f"Hardcover respondió {response.status_code}",
                status_code=response.status_code,
            )
        body: Any = response.json()
        if not isinstance(body, dict):
            raise HardcoverApiError("Respuesta inesperada de Hardcover")
        errors = body.get("errors")
        if errors and isinstance(errors, list):
            first = errors[0] if isinstance(errors[0], dict) else {}
            message = str(first.get("message", "Error de Hardcover"))
            # Un token inválido o caducado llega como error GraphQL con 200.
            lowered = message.lower()
            status = 401 if "jwt" in lowered or "auth" in lowered else None
            raise HardcoverApiError(message, status_code=status)
        me = (body.get("data") or {}).get("me")
        # Hasura devuelve `me` como lista de un elemento; se tolera objeto.
        if isinstance(me, list):
            me = me[0] if me else {}
        if not isinstance(me, dict):
            raise HardcoverApiError("Respuesta inesperada de Hardcover")
        books = me.get("user_books", [])
        return books if isinstance(books, list) else []
