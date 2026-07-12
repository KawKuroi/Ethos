"""Toque ligero y espaciado a la base de datos para que Supabase no se pause.

Los proyectos free de Supabase se pausan tras 7 días sin actividad. El ping de
UptimeRobot golpea `/health` cada pocos minutos pero no tocaba la BD; este
módulo añade una consulta mínima vía PostgREST, a lo sumo una vez por
intervalo, programada en segundo plano para no acoplar la sonda de salud a la
latencia (ni a los fallos) de Supabase.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from ethos_api.supabase_rest import SupabaseRest, get_rest

logger = logging.getLogger("ethos.keepalive")

# Una vez cada 6 horas sobra para la ventana de pausa de 7 días.
DEFAULT_INTERVAL_SECONDS = 6 * 3600.0


class DbKeepalive:
    """Ejecuta un toque mínimo a la BD, espaciado por un intervalo."""

    def __init__(
        self,
        *,
        interval_seconds: float = DEFAULT_INTERVAL_SECONDS,
        rest_provider: Callable[[], SupabaseRest | None] = get_rest,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._interval = interval_seconds
        self._rest_provider = rest_provider
        self._clock = clock
        self._last_touch: float | None = None

    def touch_if_due(self) -> str:
        """Toca la BD si el intervalo venció; devuelve el resultado.

        Resultados: "touched" (consultó), "skipped" (dentro del intervalo),
        "disabled" (sin Supabase configurado) o "error" (la consulta falló;
        se loguea y no se propaga: la sonda de salud nunca debe caer por esto).
        """
        rest = self._rest_provider()
        if rest is None:
            return "disabled"
        now = self._clock()
        if self._last_touch is not None and now - self._last_touch < self._interval:
            return "skipped"
        # Se marca antes de consultar: si Supabase falla de forma persistente,
        # no se reintenta en ráfaga con cada ping (el siguiente intento espera
        # el intervalo completo, irrelevante frente a la ventana de 7 días).
        self._last_touch = now
        try:
            rest.select("source_state", {"select": "user_id", "limit": "1"})
        except Exception:
            logger.warning("El toque de keep-alive a Supabase falló", exc_info=True)
            return "error"
        return "touched"


db_keepalive = DbKeepalive()
