"""Tests del resumen temporal y del refresco incremental de música."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ethos_api.connectors.listenbrainz.connector import (
    ListenBrainzConnector,
    ListenBrainzRawData,
)
from ethos_api.music.service import refresh_user_music
from ethos_api.music.store import InMemoryEventStore
from ethos_api.music.summary import build_music_summary
from ethos_api.schema import Category, NormalizedEvent
from ethos_api.sources_status import SyncState
from tests.music.helpers import FakeListenBrainzApi, load_listens


def _events() -> list[NormalizedEvent]:
    raw = ListenBrainzRawData(listens=load_listens())
    return ListenBrainzConnector().normalize(raw)


def test_resumen_cuenta_totales_y_top_de_la_ventana() -> None:
    events = _events()
    # `now` justo después del último listen para que caigan en la ventana.
    now = datetime.fromtimestamp(1710000300, tz=UTC) + timedelta(minutes=1)
    summary = build_music_summary(events, now=now, window_days=30)

    assert summary.scrobbles_total == 3
    assert summary.scrobbles_window == 3
    # Alvvays suena dos veces → primero en el top de artistas.
    assert summary.top_artists[0].name == "Alvvays"
    assert summary.top_artists[0].count == 2
    assert summary.top_tracks[0].count == 1
    assert summary.last_listened_at == datetime.fromtimestamp(1710000300, tz=UTC)


def test_ventana_excluye_lo_antiguo() -> None:
    events = _events()
    now = datetime.now(UTC)  # los listens de la fixture son de hace mucho
    summary = build_music_summary(events, now=now, window_days=30)
    assert summary.scrobbles_total == 3
    assert summary.scrobbles_window == 0
    assert summary.top_artists == []
    # Ventana vacía: los derivados quedan neutros y la web los oculta.
    assert summary.distinct_artists_window == 0
    assert summary.new_artists_window == 0
    assert summary.estimated_hours_window == 0.0
    assert summary.peak_weekday is None
    assert summary.top_release is None


def _listen(
    artist: str, track: str, occurred_at: datetime, release: str = ""
) -> NormalizedEvent:
    payload = {"artist": artist, "track": track}
    if release:
        payload["release"] = release
    return NormalizedEvent(
        category=Category.music,
        occurred_at=occurred_at,
        payload=payload,
        source="listenbrainz",
    )


def test_resumen_deriva_ritmo_variedad_y_descubrimientos() -> None:
    now = datetime(2026, 7, 10, 12, tzinfo=UTC)
    events = [
        # Alvvays ya sonaba antes de la ventana: no cuenta como descubrimiento.
        _listen("Alvvays", "Archie", now - timedelta(days=60), "Antisocialites"),
        _listen("Alvvays", "Dreams Tonite", now - timedelta(days=1), "Antisocialites"),
        _listen("Alvvays", "Archie", now - timedelta(days=2), "Antisocialites"),
        _listen("Men I Trust", "Show Me How", now - timedelta(days=3), "Oncle Jazz"),
    ]
    summary = build_music_summary(events, now=now, window_days=30)

    assert summary.scrobbles_window == 3
    assert summary.distinct_artists_window == 2
    assert summary.new_artists_window == 1  # Men I Trust
    # 3 escuchas x ~3,5 min = 0.2 h; 3 escuchas / 30 días = 0.1 al día.
    assert summary.estimated_hours_window == 0.2
    assert summary.avg_per_day_window == 0.1
    assert summary.top_release is not None
    assert summary.top_release.name == "Antisocialites — Alvvays"
    assert summary.top_release.count == 2
    assert summary.peak_weekday is not None
    assert summary.peak_weekday.count == 1


def test_refresco_persiste_eventos_y_estado() -> None:
    store = InMemoryEventStore()
    client = FakeListenBrainzApi()

    refresh_user_music("user-1", "oyente", client, store)

    assert store.status_for_user("user-1").state is SyncState.fresh
    assert len(store.events_for_user("user-1")) == 3
    # Primer refresco: sin min_ts.
    assert client.calls == [None]


def test_refresco_es_incremental() -> None:
    store = InMemoryEventStore()
    client = FakeListenBrainzApi()

    refresh_user_music("user-1", "oyente", client, store)
    refresh_user_music("user-1", "oyente", client, store)

    # El segundo refresco pasa el último occurred_at como min_ts y no duplica.
    assert client.calls[0] is None
    assert client.calls[1] == client.latest
    assert len(store.events_for_user("user-1")) == 3


def test_error_deja_estado_error() -> None:
    store = InMemoryEventStore()
    refresh_user_music("user-1", "oyente", FakeListenBrainzApi(fail=True), store)
    assert store.status_for_user("user-1").state is SyncState.error


def test_normalized_event_es_de_musica() -> None:
    assert _events()[0].category is Category.music
