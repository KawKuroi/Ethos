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
