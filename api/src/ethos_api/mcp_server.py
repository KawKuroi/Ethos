"""Servidor MCP de Ethos (FastMCP).

Se monta dentro del backend FastAPI para mantener un único servicio vivo
(API + MCP). El transporte streamable-HTTP se configura sin estado de sesión en
memoria (`stateless_http=True`) al construir el app ASGI en `main.py`, para
poder escalar sin afinidad de sesión.

Las tools que sirven datos del usuario exigen el token `eth_live_…` (D22) en
el header Authorization; sin token válido solo responde `ping`. Cada respuesta
reporta los KB servidos frente al contexto total (D28).
"""

from __future__ import annotations

import json

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

from ethos_api.games.context import build_games_context
from ethos_api.games.deps import get_games_store
from ethos_api.games.store import GamesStore
from ethos_api.games.summary import build_games_summary
from ethos_api.mcp_auth import get_mcp_token_store, user_from_authorization
from ethos_api.schema import ItemStatus

mcp: FastMCP = FastMCP(name="Ethos")

_AUTH_ERROR = (
    "No autenticado: configura tu token eth_live_… (Ajustes → Conectar IA) "
    "en el header Authorization"
)


def _require_user() -> str:
    """Resuelve el usuario del header Authorization o corta la tool (D22)."""
    headers = get_http_headers()
    user_id = user_from_authorization(
        headers.get("authorization"), get_mcp_token_store()
    )
    if user_id is None:
        raise ToolError(_AUTH_ERROR)
    return user_id


def _kb(payload: object) -> float:
    return round(len(json.dumps(payload, ensure_ascii=False)) / 1024, 1)


def _context_kb(user_id: str, store: GamesStore) -> float:
    """Tamaño del contexto completo, referencia de la métrica D28."""
    items = store.items_for_user(user_id)
    profile = store.profile_for_user(user_id)
    summary = build_games_summary(items, profile)
    return _kb(build_games_context(summary, items, profile))


def _served(payload: dict[str, object], user_id: str, store: GamesStore) -> dict[str, object]:
    """Añade la métrica de KB servidos vs contexto total (D28)."""
    return {
        **payload,
        "kb_served": _kb(payload),
        "kb_total": _context_kb(user_id, store),
    }


# Lógica de cada tool separada de la capa MCP para poder testearla directa.


def games_summary_payload(user_id: str, store: GamesStore) -> dict[str, object]:
    summary = build_games_summary(
        store.items_for_user(user_id),
        store.profile_for_user(user_id),
        synced_at=store.status_for_user(user_id).synced_at,
    )
    return _served(summary.model_dump(mode="json"), user_id, store)


def games_top_payload(user_id: str, store: GamesStore, limit: int) -> dict[str, object]:
    summary = build_games_summary(
        store.items_for_user(user_id), store.profile_for_user(user_id), top_limit=limit
    )
    payload: dict[str, object] = {
        "top_by_hours": [t.model_dump() for t in summary.top_by_hours]
    }
    return _served(payload, user_id, store)


def games_recent_payload(user_id: str, store: GamesStore) -> dict[str, object]:
    summary = build_games_summary(
        store.items_for_user(user_id), store.profile_for_user(user_id)
    )
    payload: dict[str, object] = {
        "recently_played": [r.model_dump() for r in summary.recently_played]
    }
    return _served(payload, user_id, store)


def profile_search_payload(user_id: str, store: GamesStore, query: str) -> dict[str, object]:
    """Búsqueda global sobre el perfil (v1: solo Juegos está activa)."""
    needle = query.strip().lower()
    matches = [
        {
            "category": item.category.value,
            "title": item.work.title,
            "status": item.status.value,
            "hours": round(item.engagement.get("playtime_minutes", 0) / 60, 1),
        }
        for item in store.items_for_user(user_id)
        if item.status is ItemStatus.in_library
        and needle
        and needle in item.work.title.lower()
    ]
    payload: dict[str, object] = {"matched": bool(matches), "results": matches[:10]}
    if not matches:
        payload["hint"] = "solo Juegos está activa en la v1"
    return _served(payload, user_id, store)


@mcp.tool
def ping() -> str:
    """Tool de prueba para verificar la conexión con el servidor MCP."""
    return "pong"


@mcp.tool(name="games.summary")
def games_summary() -> dict[str, object]:
    """Resumen agregado de Juegos: biblioteca, horas, deseados y completado."""
    return games_summary_payload(_require_user(), get_games_store())


@mcp.tool(name="games.top_by_hours")
def games_top_by_hours(limit: int = 10) -> dict[str, object]:
    """Top de juegos por horas jugadas (con completado si está calculado)."""
    return games_top_payload(_require_user(), get_games_store(), limit)


@mcp.tool(name="games.recent")
def games_recent() -> dict[str, object]:
    """Juegos con actividad en las últimas dos semanas."""
    return games_recent_payload(_require_user(), get_games_store())


@mcp.tool(name="profile.search")
def profile_search(query: str) -> dict[str, object]:
    """Busca una obra en el perfil completo (v1: categoría Juegos)."""
    return profile_search_payload(_require_user(), get_games_store(), query)


@mcp.resource("ethos://games/summary")
def games_summary_resource() -> dict[str, object]:
    """Resource con el resumen de Juegos (misma información que la tool)."""
    return games_summary_payload(_require_user(), get_games_store())
