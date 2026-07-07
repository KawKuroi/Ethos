"""Historial completo de los contextos descargables, con límite claro (D60).

Además del resumen agregado, cada contexto incluye el detalle completo de la
categoría (items o eventos) hasta `MAX_HISTORY_ENTRIES`, del más reciente al
más antiguo. El bloque describe cuánto del límite se usa (`total`, `included`,
`usage_pct`, `truncated`) para que la web y la IA sepan si el contenido está
completo o recortado.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.schema import NormalizedEvent, NormalizedItem

# Límite de entradas del historial por contexto (D60): cubre bibliotecas
# reales sin producir descargas ni respuestas MCP desmedidas.
MAX_HISTORY_ENTRIES = 1000

_EPOCH = datetime.min.replace(tzinfo=UTC)


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _parse_extra_date(item: NormalizedItem) -> datetime | None:
    # Cine y TV guarda la última reproducción en `extra` (cadena ISO).
    value = item.work.extra.get("last_watched_at")
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _recency(item: NormalizedItem) -> datetime:
    dates = [
        _as_utc(d)
        for d in (
            item.added_at,
            item.started_at,
            item.finished_at,
            _parse_extra_date(item),
        )
        if d is not None
    ]
    return max(dates, default=_EPOCH)


def item_entry(item: NormalizedItem) -> dict[str, object]:
    """Detalle completo de un item, sin campos vacíos para compactar el JSON."""
    entry: dict[str, object] = {
        "title": item.work.title,
        "status": item.status.value,
    }
    if item.work.creators:
        entry["creators"] = item.work.creators
    if item.work.year is not None:
        entry["year"] = item.work.year
    if item.rating_normalized is not None:
        entry["rating"] = item.rating_normalized
    if item.favorite:
        entry["favorite"] = True
    for field in ("added_at", "started_at", "finished_at"):
        value = getattr(item, field)
        if value is not None:
            entry[field] = value.isoformat()
    if item.engagement:
        entry["engagement"] = dict(item.engagement)
    if item.review:
        entry["review"] = item.review
    if item.tags:
        entry["tags"] = list(item.tags)
    extra = {k: v for k, v in item.work.extra.items() if v not in (None, "", [], {})}
    if extra:
        entry["extra"] = extra
    entry["source"] = item.source
    return entry


def event_entry(event: NormalizedEvent) -> dict[str, object]:
    """Detalle de un evento: la marca temporal más los campos del payload."""
    return {"occurred_at": event.occurred_at.isoformat(), **event.payload}


def history_block(
    entries: list[dict[str, object]], *, limit: int = MAX_HISTORY_ENTRIES
) -> dict[str, object]:
    """Recorta al límite y reporta el uso: total, incluidas, % y truncado."""
    limit = max(1, min(limit, MAX_HISTORY_ENTRIES))
    total = len(entries)
    included = entries[:limit]
    truncated = total > limit
    block: dict[str, object] = {
        "limit": limit,
        "total": total,
        "included": len(included),
        "usage_pct": round(len(included) * 100 / limit),
        "truncated": truncated,
        "entries": included,
    }
    if truncated:
        block["note"] = (
            f"Historial recortado al límite de {limit}: se incluyen las "
            f"{len(included)} entradas más recientes de {total}."
        )
    return block


def items_history(
    items: list[NormalizedItem], *, limit: int = MAX_HISTORY_ENTRIES
) -> dict[str, object]:
    """Historial de una categoría de obra, del más reciente al más antiguo."""
    ordered = sorted(items, key=_recency, reverse=True)
    return history_block([item_entry(i) for i in ordered], limit=limit)


def events_history(
    events: list[NormalizedEvent], *, limit: int = MAX_HISTORY_ENTRIES
) -> dict[str, object]:
    """Historial de una categoría de eventos (p. ej. listens de música)."""
    ordered = sorted(events, key=lambda e: e.occurred_at, reverse=True)
    return history_block([event_entry(e) for e in ordered], limit=limit)
