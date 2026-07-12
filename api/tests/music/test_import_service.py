"""Tests del import de eventos de música (merge, dedupe y tope)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ethos_api.music.service import MAX_IMPORTED_EVENTS, import_music_events
from ethos_api.music.store import InMemoryEventStore
from ethos_api.schema import Category, NormalizedEvent

_BASE = datetime(2026, 3, 1, 12, 0, tzinfo=UTC)


def _event(minutes: int, track: str, source: str = "spotify") -> NormalizedEvent:
    return NormalizedEvent(
        category=Category.music,
        occurred_at=_BASE + timedelta(minutes=minutes),
        payload={"artist": "Alvvays", "track": track},
        source=source,
    )


def test_importar_dos_archivos_del_mismo_proveedor_combina() -> None:
    store = InMemoryEventStore()
    import_music_events("u1", "spotify", [_event(0, "A"), _event(1, "B")], store)
    total = import_music_events("u1", "spotify", [_event(1, "B"), _event(2, "C")], store)

    # El evento repetido (mismo timestamp/artista/pista) se cuenta una vez.
    assert total == 3
    assert len(store.events_for_user("u1")) == 3
    status = store.status_for_user("u1")
    assert status.provider == "spotify"
    assert status.mode == "import"


def test_importar_otro_proveedor_reemplaza() -> None:
    store = InMemoryEventStore()
    import_music_events("u1", "spotify", [_event(0, "A"), _event(1, "B")], store)
    total = import_music_events("u1", "applemusic", [_event(5, "X", "applemusic")], store)

    assert total == 1
    events = store.events_for_user("u1")
    assert len(events) == 1
    assert events[0].source == "applemusic"


def test_el_tope_conserva_lo_mas_reciente() -> None:
    store = InMemoryEventStore()
    events = [_event(i, f"t{i}") for i in range(MAX_IMPORTED_EVENTS + 50)]
    total = import_music_events("u1", "spotify", events, store)

    assert total == MAX_IMPORTED_EVENTS
    kept = store.events_for_user("u1")
    assert len(kept) == MAX_IMPORTED_EVENTS
    # Se queda el más reciente y cae el más antiguo.
    assert kept[0].occurred_at == events[-1].occurred_at