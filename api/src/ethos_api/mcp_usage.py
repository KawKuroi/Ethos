"""Uso del MCP por usuario: llamadas por tool (estadísticas de Conectar IA).

Cada llamada autenticada a una tool del MCP incrementa el contador de esa
tool para el usuario (tabla `mcp_usage`, migración 0009; memoria en local y
CI). El registro es best-effort: un fallo al contar nunca corta la tool.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel

from ethos_api.supabase_rest import SupabaseRest, get_rest

# Tools con más llamadas que reporta el estado (suficiente para la web).
TOP_TOOLS_LIMIT = 5


class ToolCalls(BaseModel):
    """Llamadas acumuladas de una tool."""

    tool: str
    calls: int


class McpUsageStats(BaseModel):
    """Agregado del uso del MCP de un usuario (para /mcp-status)."""

    total_calls: int
    last_called_at: str | None = None
    top_tools: list[ToolCalls] = []


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _stats(rows: list[tuple[str, int, str]]) -> McpUsageStats:
    """Agrega filas (tool, calls, last_called_at) en las estadísticas."""
    top = sorted(rows, key=lambda row: row[1], reverse=True)[:TOP_TOOLS_LIMIT]
    return McpUsageStats(
        total_calls=sum(calls for _, calls, _ in rows),
        last_called_at=max((ts for _, _, ts in rows), default=None),
        top_tools=[ToolCalls(tool=tool, calls=calls) for tool, calls, _ in top],
    )


class McpUsageStore(Protocol):
    """Puerto del contador de uso del MCP."""

    def record(self, user_id: str, tool: str) -> None: ...

    def stats_for_user(self, user_id: str) -> McpUsageStats: ...


class SupabaseMcpUsageStore:
    """Respaldo en la tabla `mcp_usage` (migración 0009)."""

    _TABLE = "mcp_usage"

    def __init__(self, rest: SupabaseRest) -> None:
        self._rest = rest

    def record(self, user_id: str, tool: str) -> None:
        # Lectura + upsert (sin RPC): una carrera entre dos llamadas puede
        # perder un incremento, aceptable para estadísticas orientativas.
        rows = self._rest.select(
            self._TABLE,
            {
                "user_id": f"eq.{user_id}",
                "tool": f"eq.{tool}",
                "select": "calls",
                "limit": "1",
            },
        )
        calls = (int(rows[0]["calls"]) if rows else 0) + 1
        self._rest.upsert(
            self._TABLE,
            [
                {
                    "user_id": user_id,
                    "tool": tool,
                    "calls": calls,
                    "last_called_at": _now_iso(),
                }
            ],
            on_conflict="user_id,tool",
        )

    def stats_for_user(self, user_id: str) -> McpUsageStats:
        rows = self._rest.select(
            self._TABLE,
            {"user_id": f"eq.{user_id}", "select": "tool,calls,last_called_at"},
        )
        return _stats(
            [(str(r["tool"]), int(r["calls"]), str(r["last_called_at"])) for r in rows]
        )


class InMemoryMcpUsageStore:
    """Implementación en memoria (tests y desarrollo)."""

    def __init__(self) -> None:
        # (user_id, tool) → (calls, last_called_at)
        self._calls: dict[tuple[str, str], tuple[int, str]] = {}

    def record(self, user_id: str, tool: str) -> None:
        calls, _ = self._calls.get((user_id, tool), (0, ""))
        self._calls[(user_id, tool)] = (calls + 1, _now_iso())

    def stats_for_user(self, user_id: str) -> McpUsageStats:
        rows = [
            (tool, calls, ts)
            for (uid, tool), (calls, ts) in self._calls.items()
            if uid == user_id
        ]
        return _stats(rows)


_store: McpUsageStore | None = None


def get_mcp_usage_store() -> McpUsageStore:
    """Supabase si está configurado; memoria en local/CI."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseMcpUsageStore(rest) if rest else InMemoryMcpUsageStore()
    return _store
