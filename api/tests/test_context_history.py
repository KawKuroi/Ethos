"""Tests del historial de los contextos con límite y metadatos de uso (D60)."""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.context_history import (
    MAX_HISTORY_ENTRIES,
    event_entry,
    events_history,
    item_entry,
    items_history,
)
from ethos_api.schema import Category, ItemStatus, NormalizedEvent, NormalizedItem, Work


def _item(title: str, *, finished: datetime | None = None, **kwargs: object) -> NormalizedItem:
    return NormalizedItem(
        work=Work(title=title, **kwargs.pop("work", {})),  # type: ignore[arg-type]
        category=Category.books,
        status=ItemStatus.consumed,
        finished_at=finished,
        source="test",
        **kwargs,  # type: ignore[arg-type]
    )


def _event(at: datetime, artist: str) -> NormalizedEvent:
    return NormalizedEvent(
        category=Category.music,
        occurred_at=at,
        payload={"artist": artist, "track": "Canción"},
        source="test",
    )


def _entries(history: dict[str, object]) -> list[dict[str, object]]:
    """Estrecha `entries` (tipado `object` en el bloque) para los asserts."""
    entries = history["entries"]
    assert isinstance(entries, list)
    return entries


def test_item_entry_completo_y_sin_campos_vacios() -> None:
    item = NormalizedItem(
        work=Work(
            title="Dune",
            creators=["Frank Herbert"],
            year=1965,
            extra={"pages": 412, "empty": ""},
        ),
        category=Category.books,
        status=ItemStatus.consumed,
        rating_normalized=90,
        favorite=True,
        finished_at=datetime(2026, 1, 5, tzinfo=UTC),
        engagement={"reads": 2},
        review="Enorme.",
        tags=["sci-fi"],
        source="goodreads",
    )
    entry = item_entry(item)

    assert entry["title"] == "Dune"
    assert entry["creators"] == ["Frank Herbert"]
    assert entry["rating"] == 90
    assert entry["favorite"] is True
    assert entry["engagement"] == {"reads": 2}
    assert entry["extra"] == {"pages": 412}
    # Los campos sin valor no viajan: compacta el JSON del contexto.
    assert "started_at" not in entry
    assert "added_at" not in entry


def test_items_history_ordena_por_recencia_y_reporta_uso() -> None:
    items = [
        _item("Antiguo", finished=datetime(2020, 1, 1, tzinfo=UTC)),
        _item("Reciente", finished=datetime(2026, 6, 1, tzinfo=UTC)),
        _item("Sin fecha"),
    ]
    history = items_history(items)

    assert history["limit"] == MAX_HISTORY_ENTRIES
    assert history["total"] == 3
    assert history["included"] == 3
    assert history["usage_pct"] == 0  # 3 de 1000 redondea a 0 %.
    assert history["truncated"] is False
    assert "note" not in history
    titles = [e["title"] for e in _entries(history)]
    assert titles == ["Reciente", "Antiguo", "Sin fecha"]


def test_items_history_trunca_al_limite_y_avisa() -> None:
    items = [
        _item(f"Libro {i}", finished=datetime(2026, 1, 1 + i, tzinfo=UTC))
        for i in range(4)
    ]
    history = items_history(items, limit=2)

    assert history["limit"] == 2
    assert history["total"] == 4
    assert history["included"] == 2
    assert history["usage_pct"] == 100
    assert history["truncated"] is True
    assert "recortado al límite" in str(history["note"])
    # Conserva las más recientes.
    assert [e["title"] for e in _entries(history)] == ["Libro 3", "Libro 2"]


def test_events_history_ordena_desc_y_lleva_payload() -> None:
    events = [
        _event(datetime(2026, 6, 1, tzinfo=UTC), "A"),
        _event(datetime(2026, 6, 3, tzinfo=UTC), "B"),
    ]
    history = events_history(events)

    assert history["total"] == 2
    first = _entries(history)[0]
    assert first["artist"] == "B"
    assert first["occurred_at"] == "2026-06-03T00:00:00+00:00"
    assert event_entry(events[0])["track"] == "Canción"


def test_recencia_lee_last_watched_at_de_extra() -> None:
    visto = _item("Película")
    visto.work.extra["last_watched_at"] = "2026-06-30T10:00:00Z"
    history = items_history([_item("Sin fecha"), visto])

    assert next(e["title"] for e in _entries(history)) == "Película"
