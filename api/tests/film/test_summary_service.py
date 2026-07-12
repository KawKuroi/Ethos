"""Tests del resumen y del refresco de Cine y TV."""

from __future__ import annotations

from ethos_api.connectors.trakt.connector import TraktConnector, TraktRawData
from ethos_api.film.service import refresh_user_film
from ethos_api.film.store import InMemoryFilmStore
from ethos_api.film.summary import build_film_summary
from ethos_api.schema import Category, ItemStatus, NormalizedItem, Work
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


def _rated_movie(
    title: str,
    *,
    year: int | None = None,
    rating: int | None = None,
    plays: int = 1,
    tags: list[str] | None = None,
) -> NormalizedItem:
    """Obra como la deja un import de Letterboxd/IMDb: nota, año y géneros."""
    return NormalizedItem(
        work=Work(title=title, year=year, extra={"media_type": "movie"}),
        category=Category.film,
        status=ItemStatus.consumed,
        rating_normalized=rating,
        engagement={"plays": plays},
        tags=tags or [],
        source="letterboxd",
    )


def test_resumen_agrega_notas_generos_y_decada() -> None:
    items = [
        _rated_movie("Whiplash", year=2014, rating=100, tags=["Drama"]),
        _rated_movie("La La Land", year=2016, rating=80, plays=2, tags=["Drama"]),
        _rated_movie("Alien", year=1979, rating=90, tags=["Sci-Fi"]),
        _rated_movie("Batman & Robin", year=1997, rating=20),
        # Sin nota: cuenta para la década pero no para la media.
        _rated_movie("Heat", year=1995),
    ]
    summary = build_film_summary(items, None)

    assert summary.mean_rating == 72.5
    assert summary.rated_count == 4
    assert summary.top_rated[0].title == "Whiplash"
    assert summary.top_rated[0].rating == 100
    # 100 y 90 → 5★; 80 → 4★; 20 → 1★. Siempre las cinco franjas.
    buckets = {b.stars: b.count for b in summary.rating_buckets}
    assert buckets == {1: 1, 2: 0, 3: 0, 4: 1, 5: 2}
    # Solo La La Land tiene más de una reproducción.
    assert summary.rewatched_count == 1
    assert summary.top_genres[0].name == "Drama"
    assert summary.top_genres[0].works == 2
    # 1990 y 2010 empatan a 2 obras: gana la década más reciente.
    assert summary.favorite_decade == 2010


def test_resumen_sin_notas_deja_campos_vacios() -> None:
    # Trakt no trae notas ni géneros: los campos quedan neutros y la web
    # los oculta.
    summary = build_film_summary(TraktConnector().normalize(_raw()), None)
    assert summary.mean_rating is None
    assert summary.rated_count == 0
    assert summary.rating_buckets == []
    assert summary.top_rated == []
    assert summary.top_genres == []


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
