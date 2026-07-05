"""Tests del resumen y del refresco de Cine y TV."""

from __future__ import annotations

from ethos_api.connectors.trakt.connector import TraktConnector, TraktRawData
from ethos_api.film.service import refresh_user_film
from ethos_api.film.store import InMemoryFilmStore
from ethos_api.film.summary import build_film_summary
from ethos_api.sources_status import SyncState
from tests.film.helpers import SAMPLE_MOVIES, SAMPLE_SHOWS, SAMPLE_STATS, FakeTraktApi


def _raw() -> TraktRawData:
    return TraktRawData(
        watched_movies=SAMPLE_MOVIES, watched_shows=SAMPLE_SHOWS, stats=SAMPLE_STATS
    )


def test_resumen_agrega_totales_y_tops() -> None:
    connector = TraktConnector()
    raw = _raw()
    summary = build_film_summary(connector.normalize(raw), connector.stats(raw))

    assert summary.movies_watched == 2
    assert summary.shows_watched == 1
    assert summary.episodes_watched == 5
    # (260 + 2790) / 60 = 50,8 h.
    assert summary.hours == 50.8
    # Inception (3 plays) por delante de Arrival (1 play).
    assert summary.top_movies[0].title == "Inception"
    assert summary.top_shows[0].episodes_watched == 5
    # El más reciente por last_watched_at es Breaking Bad (2026-07-01).
    assert summary.recently_watched[0].title == "Breaking Bad"
    assert summary.recently_watched[0].media_type == "show"


def test_resumen_sin_stats_usa_conteos_de_items() -> None:
    connector = TraktConnector()
    summary = build_film_summary(connector.normalize(_raw()), None)
    assert summary.movies_watched == 2
    assert summary.shows_watched == 1
    assert summary.hours == 0.0


def test_refresco_persiste_items_stats_y_estado() -> None:
    store = InMemoryFilmStore()
    client = FakeTraktApi()

    refresh_user_film("user-1", "cinefilo", client, store)

    assert store.status_for_user("user-1").state is SyncState.fresh
    assert len(store.items_for_user("user-1")) == 3
    assert store.stats_for_user("user-1") is not None
    assert client.calls == ["movies", "shows", "stats"]


def test_perfil_privado_deja_estado_private() -> None:
    store = InMemoryFilmStore()
    refresh_user_film("user-1", "privado", FakeTraktApi(status_code=401), store)
    estado = store.status_for_user("user-1")
    assert estado.state is SyncState.private
    assert estado.detail is not None


def test_error_generico_deja_estado_error() -> None:
    store = InMemoryFilmStore()
    refresh_user_film("user-1", "cinefilo", FakeTraktApi(fail=True), store)
    assert store.status_for_user("user-1").state is SyncState.error
