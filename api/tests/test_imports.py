"""Tests del import genérico con autodetección (D49/D62)."""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.books.deps import get_books_store
from ethos_api.books.store import InMemoryBooksStore
from ethos_api.film.deps import get_film_store
from ethos_api.film.store import InMemoryFilmStore
from ethos_api.imports.detection import detect_import
from ethos_api.main import app
from ethos_api.music.deps import get_event_store
from ethos_api.music.store import InMemoryEventStore
from ethos_api.schema import Category
from tests.books.helpers import GOODREADS_CSV, STORYGRAPH_CSV
from tests.helpers import auth_headers

LETTERBOXD_DIARY = (
    "Date,Name,Year,Letterboxd URI,Rating,Rewatch,Tags,Watched Date\n"
    "2026-03-01,Paddington 2,2017,https://boxd.it/abc1,5,,cozy,2026-02-28\n"
)

LETTERBOXD_WATCHED = (
    "Date,Name,Year,Letterboxd URI\n"
    "2026-02-01,Aftersun,2022,https://boxd.it/def2\n"
)

IMDB_RATINGS = (
    "Const,Your Rating,Date Rated,Title,Title Type,IMDb Rating,Runtime (mins),"
    "Year,Genres,Num Votes,Release Date,Directors\n"
    "tt0111161,10,2026-01-05,The Shawshank Redemption,Movie,9.3,142,1994,"
    "Drama,3000000,1994-09-23,Frank Darabont\n"
)

SPOTIFY_JSON = json.dumps(
    [
        {
            "ts": "2026-03-01T18:22:05Z",
            "ms_played": 215000,
            "master_metadata_track_name": "Belinda Says",
            "master_metadata_album_artist_name": "Alvvays",
            "master_metadata_album_album_name": "Blue Rev",
        }
    ]
)

APPLEMUSIC_CSV = (
    "Track Description,Date Played,Play Duration Milliseconds,Play Count\n"
    "Alvvays - Belinda Says,20260301,215000,3\n"
)


def test_detecta_el_export_de_cada_proveedor() -> None:
    casos = [
        (GOODREADS_CSV, "goodreads", Category.books),
        (STORYGRAPH_CSV, "storygraph", Category.books),
        (LETTERBOXD_DIARY, "letterboxd", Category.film),
        (LETTERBOXD_WATCHED, "letterboxd", Category.film),
        (IMDB_RATINGS, "imdb", Category.film),
        (SPOTIFY_JSON, "spotify", Category.music),
        (APPLEMUSIC_CSV, "applemusic", Category.music),
    ]
    for texto, provider, category in casos:
        signature = detect_import(texto)
        assert signature is not None, provider
        assert signature.provider == provider
        assert signature.category is category


def test_archivo_desconocido_no_se_detecta() -> None:
    assert detect_import("col1,col2\n1,2\n") is None
    assert detect_import("") is None
    assert detect_import("no es un csv") is None
    assert detect_import("[1, 2, 3]") is None
    assert detect_import("[no json") is None


@pytest.fixture
def client(
    jwt_secret: str,
) -> Iterator[tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore]]:
    books = InMemoryBooksStore()
    film = InMemoryFilmStore()
    events = InMemoryEventStore()
    app.dependency_overrides[get_books_store] = lambda: books
    app.dependency_overrides[get_film_store] = lambda: film
    app.dependency_overrides[get_event_store] = lambda: events
    with TestClient(app) as test_client:
        yield test_client, books, film, events
    app.dependency_overrides.clear()


def _post(test_client: TestClient, texto: str) -> dict[str, object]:
    respuesta = test_client.post(
        "/imports",
        content=texto.encode(),
        headers={**auth_headers(), "Content-Type": "text/plain"},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_import_generico_detecta_y_delega(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, books, _, _ = client
    datos = _post(test_client, GOODREADS_CSV)
    assert datos["provider"] == "goodreads"
    assert datos["category"] == "books"
    assert datos["items"] == 4
    assert len(books.items_for_user("user-1")) == 4


def test_import_de_letterboxd_puebla_cine(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, _, film, _ = client
    datos = _post(test_client, LETTERBOXD_DIARY)
    assert datos["provider"] == "letterboxd"
    assert datos["category"] == "film"
    # Subir un segundo CSV del mismo export combina por obra (no duplica).
    datos = _post(test_client, LETTERBOXD_WATCHED)
    assert datos["items"] == 2
    assert len(film.items_for_user("user-1")) == 2
    assert film.status_for_user("user-1").provider == "letterboxd"


def test_import_de_imdb_reemplaza_a_letterboxd(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, _, film, _ = client
    _post(test_client, LETTERBOXD_DIARY)
    datos = _post(test_client, IMDB_RATINGS)
    # Proveedor distinto: reemplaza el conjunto (D4).
    assert datos["items"] == 1
    assert len(film.items_for_user("user-1")) == 1
    assert film.status_for_user("user-1").provider == "imdb"


def test_import_de_spotify_puebla_musica(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, _, _, events = client
    datos = _post(test_client, SPOTIFY_JSON)
    assert datos["provider"] == "spotify"
    assert datos["category"] == "music"
    assert len(events.events_for_user("user-1")) == 1
    status = events.status_for_user("user-1")
    assert status.provider == "spotify"
    assert status.mode == "import"


def test_import_de_applemusic_puebla_musica(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, _, _, events = client
    datos = _post(test_client, APPLEMUSIC_CSV)
    assert datos["provider"] == "applemusic"
    assert len(events.events_for_user("user-1")) == 1


def test_import_generico_desconocido_da_422_con_guia(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, _, _, _ = client
    respuesta = test_client.post(
        "/imports",
        content=b"col1,col2\n1,2\n",
        headers={**auth_headers(), "Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 422
    assert "Goodreads" in respuesta.json()["detail"]


def test_import_generico_requiere_sesion(
    client: tuple[TestClient, InMemoryBooksStore, InMemoryFilmStore, InMemoryEventStore],
) -> None:
    test_client, _, _, _ = client
    assert test_client.post("/imports", content=b"x").status_code == 401
