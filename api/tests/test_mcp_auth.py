"""Tests de la auth del MCP (D22) y de las tools de datos (D28)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ethos_api.anime.store import InMemoryAnimeStore
from ethos_api.books.store import InMemoryBooksStore
from ethos_api.film.store import InMemoryFilmStore
from ethos_api.games.store import InMemoryGamesStore
from ethos_api.main import app
from ethos_api.mcp_auth import InMemoryMcpTokenStore, user_from_authorization
from ethos_api.mcp_server import (
    games_summary_payload,
    games_top_payload,
    profile_search_payload,
)
from ethos_api.music.store import InMemoryEventStore
from tests.games.helpers import FakeSteamApi
from tests.helpers import auth_headers


def test_emitir_y_resolver_token() -> None:
    store = InMemoryMcpTokenStore()
    token = store.issue("user-1")
    assert token.startswith("eth_live_")
    assert store.resolve(token) == "user-1"


def test_emitir_de_nuevo_rota_el_anterior() -> None:
    store = InMemoryMcpTokenStore()
    primero = store.issue("user-1")
    segundo = store.issue("user-1")
    assert store.resolve(primero) is None
    assert store.resolve(segundo) == "user-1"


def test_resolver_rechaza_tokens_ajenos() -> None:
    store = InMemoryMcpTokenStore()
    store.issue("user-1")
    assert store.resolve("eth_live_invento") is None
    assert store.resolve("otro-esquema") is None


def test_user_from_authorization() -> None:
    store = InMemoryMcpTokenStore()
    token = store.issue("user-1")
    assert user_from_authorization(f"Bearer {token}", store) == "user-1"
    assert user_from_authorization(token, store) is None
    assert user_from_authorization(None, store) is None


@pytest.fixture
def api_client(jwt_secret: str) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_endpoint_emite_token_con_sesion(api_client: TestClient) -> None:
    respuesta = api_client.post("/mcp-token", headers=auth_headers())
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["token"].startswith("eth_live_")
    assert datos["endpoint"].endswith("/mcp/")


def test_endpoint_requiere_sesion(api_client: TestClient) -> None:
    assert api_client.post("/mcp-token").status_code == 401


def test_mcp_status_requiere_sesion(api_client: TestClient) -> None:
    assert api_client.get("/mcp-status").status_code == 401


def test_mcp_status_refleja_token_y_oauth(api_client: TestClient) -> None:
    """El estado pasa a real conforme el usuario emite token o autoriza vía OAuth."""
    from ethos_api.oauth.deps import get_oauth_token_store

    headers = auth_headers("user-status")

    inicial = api_client.get("/mcp-status", headers=headers).json()
    assert inicial["oauth_connected"] is False
    assert inicial["token_issued"] is False
    assert inicial["endpoint"].endswith("/mcp/")

    api_client.post("/mcp-token", headers=headers)
    con_token = api_client.get("/mcp-status", headers=headers).json()
    assert con_token["token_issued"] is True
    assert con_token["oauth_connected"] is False

    get_oauth_token_store().issue_pair("user-status", "client-x")
    con_oauth = api_client.get("/mcp-status", headers=headers).json()
    assert con_oauth["oauth_connected"] is True


def _store_poblado(user: str = "user-1") -> InMemoryGamesStore:
    from ethos_api.games.service import refresh_user_games

    store = InMemoryGamesStore()
    refresh_user_games(user, "765", FakeSteamApi(), store)
    return store


def test_payload_del_resumen_reporta_kb() -> None:
    store = _store_poblado()
    payload = games_summary_payload("user-1", store)
    assert payload["games"] == 2
    kb_served, kb_total = payload["kb_served"], payload["kb_total"]
    assert isinstance(kb_served, float) and kb_served > 0
    assert isinstance(kb_total, float) and kb_total > 0


def test_payload_del_top_respeta_limit() -> None:
    store = _store_poblado()
    payload = games_top_payload("user-1", store, limit=1)
    top = payload["top_by_hours"]
    assert isinstance(top, list)
    assert len(top) == 1
    assert top[0]["title"] == "Dota 2"


def test_profile_search_encuentra_y_degrada() -> None:
    games = _store_poblado()
    film = InMemoryFilmStore()
    anime = InMemoryAnimeStore()
    books = InMemoryBooksStore()

    con_match = profile_search_payload("user-1", games, film, anime, books, "fortress")
    assert con_match["matched"] is True

    sin_match = profile_search_payload("user-1", games, film, anime, books, "zelda")
    assert sin_match["matched"] is False
    assert "hint" in sin_match


def test_profile_search_cruza_categorias() -> None:
    from ethos_api.books.service import import_goodreads_csv
    from tests.books.helpers import GOODREADS_CSV

    games = _store_poblado()
    film = InMemoryFilmStore()
    anime = InMemoryAnimeStore()
    books = InMemoryBooksStore()
    import_goodreads_csv("user-1", GOODREADS_CSV, books)

    payload = profile_search_payload("user-1", games, film, anime, books, "dune")
    assert payload["matched"] is True
    results = payload["results"]
    assert isinstance(results, list)
    assert results[0]["category"] == "books"
    assert results[0]["title"] == "Dune"


@pytest.mark.anyio
async def test_tools_de_datos_exigen_token() -> None:
    """En transporte in-memory no hay headers: la tool debe rechazar (D22)."""
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="No autenticado"):
            await client.call_tool("games_summary", {})


@pytest.mark.anyio
async def test_ping_sigue_abierto() -> None:
    from fastmcp import Client

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        result = await client.call_tool("ping", {})
        assert result.data == "pong"


def _music_store_poblado(user: str = "user-1") -> InMemoryEventStore:
    from ethos_api.music.service import refresh_user_music
    from tests.music.helpers import FakeListenBrainzApi

    store = InMemoryEventStore()
    refresh_user_music(user, "oyente", FakeListenBrainzApi(), store)
    return store


def test_payload_de_musica_reporta_kb_y_ventana() -> None:
    from ethos_api.mcp_server import music_summary_payload, music_top_artists_payload

    store = _music_store_poblado()
    resumen = music_summary_payload("user-1", store)
    assert resumen["scrobbles_total"] == 3
    kb_served, kb_total = resumen["kb_served"], resumen["kb_total"]
    assert isinstance(kb_served, float) and kb_served > 0
    assert isinstance(kb_total, float) and kb_total > 0

    top = music_top_artists_payload("user-1", store, limit=5)
    artistas = top["top_artists"]
    assert isinstance(artistas, list)
    assert artistas[0]["name"] == "Alvvays"


def test_music_recent_respeta_limit() -> None:
    from ethos_api.mcp_server import music_recent_payload

    store = _music_store_poblado()
    payload = music_recent_payload("user-1", store, limit=2)
    recent = payload["recent"]
    assert isinstance(recent, list)
    assert len(recent) == 2


@pytest.mark.anyio
async def test_music_summary_tool_exige_token() -> None:
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="No autenticado"):
            await client.call_tool("music_summary", {})


def _film_store_poblado(user: str = "user-1") -> InMemoryFilmStore:
    from ethos_api.film.service import refresh_user_film
    from tests.film.helpers import FakeTraktApi

    store = InMemoryFilmStore()
    refresh_user_film(user, "cinefilo", FakeTraktApi(), store)
    return store


def test_payload_de_cine_reporta_kb_y_tops() -> None:
    from ethos_api.mcp_server import film_summary_payload, film_top_movies_payload

    store = _film_store_poblado()
    resumen = film_summary_payload("user-1", store)
    assert resumen["movies_watched"] == 2
    kb_served, kb_total = resumen["kb_served"], resumen["kb_total"]
    assert isinstance(kb_served, float) and kb_served > 0
    assert isinstance(kb_total, float) and kb_total > 0

    top = film_top_movies_payload("user-1", store, limit=1)
    peliculas = top["top_movies"]
    assert isinstance(peliculas, list)
    assert len(peliculas) == 1
    assert peliculas[0]["title"] == "Inception"


def test_film_recent_respeta_limit() -> None:
    from ethos_api.mcp_server import film_recent_payload

    store = _film_store_poblado()
    payload = film_recent_payload("user-1", store, limit=1)
    recent = payload["recently_watched"]
    assert isinstance(recent, list)
    assert len(recent) == 1


@pytest.mark.anyio
async def test_film_summary_tool_exige_token() -> None:
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="No autenticado"):
            await client.call_tool("film_summary", {})


def _anime_store_poblado(user: str = "user-1") -> InMemoryAnimeStore:
    from ethos_api.anime.service import refresh_user_anime
    from tests.anime.helpers import FakeAniListApi

    store = InMemoryAnimeStore()
    refresh_user_anime(user, "otaku", FakeAniListApi(), store)
    return store


def test_payload_de_anime_reporta_kb_y_tops() -> None:
    from ethos_api.mcp_server import (
        anime_current_payload,
        anime_summary_payload,
        anime_top_rated_payload,
    )

    store = _anime_store_poblado()
    resumen = anime_summary_payload("user-1", store)
    assert resumen["anime_watched"] == 1
    assert resumen["chapters_read"] == 205
    kb_served, kb_total = resumen["kb_served"], resumen["kb_total"]
    assert isinstance(kb_served, float) and kb_served > 0
    assert isinstance(kb_total, float) and kb_total > 0

    top = anime_top_rated_payload("user-1", store, limit=1)
    entradas = top["top_rated"]
    assert isinstance(entradas, list)
    assert len(entradas) == 1
    assert entradas[0]["title"] == "Berserk"

    en_curso = anime_current_payload("user-1", store, limit=5)
    current = en_curso["current"]
    assert isinstance(current, list)
    assert current[0]["title"] == "One Piece"


def _books_store_poblado(user: str = "user-1") -> InMemoryBooksStore:
    from ethos_api.books.service import import_goodreads_csv
    from tests.books.helpers import GOODREADS_CSV

    store = InMemoryBooksStore()
    import_goodreads_csv(user, GOODREADS_CSV, store)
    return store


def test_payload_de_libros_reporta_kb_y_lecturas() -> None:
    from ethos_api.mcp_server import (
        books_currently_reading_payload,
        books_summary_payload,
        books_top_authors_payload,
    )

    store = _books_store_poblado()
    resumen = books_summary_payload("user-1", store)
    assert resumen["books_read"] == 2
    kb_served, kb_total = resumen["kb_served"], resumen["kb_total"]
    assert isinstance(kb_served, float) and kb_served > 0
    assert isinstance(kb_total, float) and kb_total > 0

    en_curso = books_currently_reading_payload("user-1", store)
    reading = en_curso["currently_reading"]
    assert isinstance(reading, list)
    assert reading[0]["title"] == "Project Hail Mary"

    autores = books_top_authors_payload("user-1", store, limit=1)
    top = autores["top_authors"]
    assert isinstance(top, list)
    assert len(top) == 1


@pytest.mark.anyio
async def test_anime_y_books_tools_exigen_token() -> None:
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    from ethos_api.mcp_server import mcp

    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="No autenticado"):
            await client.call_tool("anime_summary", {})
        with pytest.raises(ToolError, match="No autenticado"):
            await client.call_tool("books_summary", {})
