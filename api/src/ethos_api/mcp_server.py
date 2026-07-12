"""Servidor MCP de Ethos (FastMCP).

Se monta dentro del backend FastAPI para mantener un único servicio vivo
(API + MCP). El transporte streamable-HTTP se configura sin estado de sesión en
memoria (`stateless_http=True`) al construir el app ASGI en `main.py`, para
poder escalar sin afinidad de sesión.

Las tools que sirven datos del usuario exigen el token `eth_live_…` (D22) en
el header Authorization; sin token válido solo responde `ping`. Cada respuesta
reporta los KB servidos frente al contexto total (D28).
"""

from __future__ import annotations

import json

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

from ethos_api.anime.context import build_anime_context
from ethos_api.anime.deps import get_anime_store
from ethos_api.anime.store import AnimeStore
from ethos_api.anime.summary import build_anime_summary
from ethos_api.books.context import build_books_context
from ethos_api.books.deps import get_books_store
from ethos_api.books.store import BooksStore
from ethos_api.books.summary import build_books_summary
from ethos_api.context_history import (
    MAX_HISTORY_ENTRIES,
    events_history,
    items_history,
)
from ethos_api.film.context import build_film_context
from ethos_api.film.deps import get_film_store
from ethos_api.film.store import FilmStore
from ethos_api.film.summary import build_film_summary
from ethos_api.games.context import build_games_context
from ethos_api.games.deps import get_games_store
from ethos_api.games.store import GamesStore
from ethos_api.games.summary import build_games_summary
from ethos_api.mcp_auth import resolve_bearer_user
from ethos_api.music.deps import get_event_store
from ethos_api.music.store import EventStore
from ethos_api.music.summary import build_music_summary
from ethos_api.schema import ItemStatus, NormalizedItem

mcp: FastMCP = FastMCP(name="Ethos")

_AUTH_ERROR = (
    "No autenticado: configura tu token eth_live_… (Ajustes → Conectar IA) "
    "en el header Authorization"
)


def _require_user() -> str:
    """Resuelve el usuario del header Authorization o corta la tool (D22/D56).

    Acepta el token legacy `eth_live_…` y los access tokens OAuth
    `eth_oauth_…`. El middleware del desafío 401 ya filtró en el transporte;
    esto es defensa en profundidad.
    """
    headers = get_http_headers()
    user_id = resolve_bearer_user(headers.get("authorization"))
    if user_id is None:
        raise ToolError(_AUTH_ERROR)
    return user_id


def _kb(payload: object) -> float:
    return round(len(json.dumps(payload, ensure_ascii=False)) / 1024, 1)


def _games_context_kb(user_id: str, store: GamesStore) -> float:
    """Tamaño del contexto completo de Juegos, referencia de la métrica D28."""
    items = store.items_for_user(user_id)
    profile = store.profile_for_user(user_id)
    summary = build_games_summary(items, profile)
    return _kb(build_games_context(summary, items, profile))


def _served(payload: dict[str, object], kb_total: float) -> dict[str, object]:
    """Añade la métrica de KB servidos vs contexto total (D28)."""
    return {
        **payload,
        "kb_served": _kb(payload),
        "kb_total": kb_total,
    }


# Lógica de cada tool separada de la capa MCP para poder testearla directa.


def games_summary_payload(user_id: str, store: GamesStore) -> dict[str, object]:
    summary = build_games_summary(
        store.items_for_user(user_id),
        store.profile_for_user(user_id),
        synced_at=store.status_for_user(user_id).synced_at,
    )
    return _served(summary.model_dump(mode="json"), _games_context_kb(user_id, store))


def games_top_payload(user_id: str, store: GamesStore, limit: int) -> dict[str, object]:
    summary = build_games_summary(
        store.items_for_user(user_id), store.profile_for_user(user_id), top_limit=limit
    )
    payload: dict[str, object] = {
        "top_by_hours": [t.model_dump() for t in summary.top_by_hours]
    }
    return _served(payload, _games_context_kb(user_id, store))


def games_recent_payload(user_id: str, store: GamesStore) -> dict[str, object]:
    summary = build_games_summary(
        store.items_for_user(user_id), store.profile_for_user(user_id)
    )
    payload: dict[str, object] = {
        "recently_played": [r.model_dump() for r in summary.recently_played]
    }
    return _served(payload, _games_context_kb(user_id, store))


def games_history_payload(
    user_id: str, store: GamesStore, limit: int
) -> dict[str, object]:
    """Biblioteca completa hasta el límite (la wishlist viaja aparte, D32/D60)."""
    items = [
        i
        for i in store.items_for_user(user_id)
        if i.status is not ItemStatus.wishlist
    ]
    payload: dict[str, object] = {"history": items_history(items, limit=limit)}
    return _served(payload, _games_context_kb(user_id, store))


def _search_result(item: NormalizedItem) -> dict[str, object]:
    result: dict[str, object] = {
        "category": item.category.value,
        "title": item.work.title,
        "status": item.status.value,
    }
    minutes = item.engagement.get("playtime_minutes", 0)
    if minutes:
        result["hours"] = round(minutes / 60, 1)
    return result


def profile_search_payload(
    user_id: str,
    games: GamesStore,
    film: FilmStore,
    anime: AnimeStore,
    books: BooksStore,
    query: str,
) -> dict[str, object]:
    """Búsqueda por título sobre las categorías de obra del perfil."""
    needle = query.strip().lower()
    matches: list[dict[str, object]] = []
    stores = (games, film, anime, books)
    for store in stores:
        for item in store.items_for_user(user_id):
            if needle and needle in item.work.title.lower():
                matches.append(_search_result(item))
    payload: dict[str, object] = {"matched": bool(matches), "results": matches[:10]}
    if not matches:
        payload["hint"] = (
            "busca por título entre Juegos, Cine y TV, Anime y manga y Libros; "
            "Música se consulta con las tools music_*"
        )
    kb_total = round(
        _games_context_kb(user_id, games)
        + _film_context_kb(user_id, film)
        + _anime_context_kb(user_id, anime)
        + _books_context_kb(user_id, books),
        1,
    )
    return _served(payload, kb_total)


def _music_context_kb(user_id: str, store: EventStore) -> float:
    """Tamaño del contexto completo de Música, referencia de la métrica D28."""
    from ethos_api.music.context import build_music_context

    events = store.events_for_user(user_id)
    summary = build_music_summary(events)
    return _kb(build_music_context(summary, events))


def music_summary_payload(user_id: str, store: EventStore) -> dict[str, object]:
    summary = build_music_summary(store.events_for_user(user_id))
    return _served(summary.model_dump(mode="json"), _music_context_kb(user_id, store))


def music_top_artists_payload(
    user_id: str, store: EventStore, limit: int
) -> dict[str, object]:
    summary = build_music_summary(store.events_for_user(user_id), top_limit=limit)
    payload: dict[str, object] = {
        "window_days": summary.window_days,
        "top_artists": [a.model_dump() for a in summary.top_artists],
    }
    return _served(payload, _music_context_kb(user_id, store))


def music_recent_payload(
    user_id: str, store: EventStore, limit: int
) -> dict[str, object]:
    """Últimos listens (el store los guarda del más reciente al más antiguo)."""
    events = store.events_for_user(user_id)[:limit]
    payload: dict[str, object] = {
        "recent": [
            {"occurred_at": e.occurred_at.isoformat(), **e.payload} for e in events
        ]
    }
    return _served(payload, _music_context_kb(user_id, store))


def music_history_payload(
    user_id: str, store: EventStore, limit: int
) -> dict[str, object]:
    """Listens completos hasta el límite, con metadatos de uso (D60)."""
    payload: dict[str, object] = {
        "history": events_history(store.events_for_user(user_id), limit=limit)
    }
    return _served(payload, _music_context_kb(user_id, store))


def _film_context_kb(user_id: str, store: FilmStore) -> float:
    """Tamaño del contexto completo de Cine y TV, referencia de la métrica D28."""
    items = store.items_for_user(user_id)
    summary = build_film_summary(items, store.stats_for_user(user_id))
    return _kb(build_film_context(summary, items))


def film_summary_payload(user_id: str, store: FilmStore) -> dict[str, object]:
    summary = build_film_summary(
        store.items_for_user(user_id),
        store.stats_for_user(user_id),
        synced_at=store.status_for_user(user_id).synced_at,
    )
    return _served(summary.model_dump(mode="json"), _film_context_kb(user_id, store))


def film_top_movies_payload(
    user_id: str, store: FilmStore, limit: int
) -> dict[str, object]:
    summary = build_film_summary(
        store.items_for_user(user_id), store.stats_for_user(user_id), top_limit=limit
    )
    payload: dict[str, object] = {
        "top_movies": [m.model_dump(mode="json") for m in summary.top_movies]
    }
    return _served(payload, _film_context_kb(user_id, store))


def film_recent_payload(user_id: str, store: FilmStore, limit: int) -> dict[str, object]:
    summary = build_film_summary(
        store.items_for_user(user_id), store.stats_for_user(user_id), top_limit=limit
    )
    payload: dict[str, object] = {
        "recently_watched": [
            r.model_dump(mode="json") for r in summary.recently_watched
        ]
    }
    return _served(payload, _film_context_kb(user_id, store))


def film_history_payload(
    user_id: str, store: FilmStore, limit: int
) -> dict[str, object]:
    """Historial completo de Cine y TV hasta el límite (D60)."""
    payload: dict[str, object] = {
        "history": items_history(store.items_for_user(user_id), limit=limit)
    }
    return _served(payload, _film_context_kb(user_id, store))


def _anime_context_kb(user_id: str, store: AnimeStore) -> float:
    """Tamaño del contexto completo de Anime, referencia de la métrica D28."""
    items = store.items_for_user(user_id)
    summary = build_anime_summary(items)
    return _kb(build_anime_context(summary, items))


def anime_summary_payload(user_id: str, store: AnimeStore) -> dict[str, object]:
    summary = build_anime_summary(
        store.items_for_user(user_id),
        synced_at=store.status_for_user(user_id).synced_at,
    )
    return _served(summary.model_dump(mode="json"), _anime_context_kb(user_id, store))


def anime_top_rated_payload(
    user_id: str, store: AnimeStore, limit: int
) -> dict[str, object]:
    summary = build_anime_summary(store.items_for_user(user_id), top_limit=limit)
    payload: dict[str, object] = {
        "top_rated": [t.model_dump(mode="json") for t in summary.top_rated]
    }
    return _served(payload, _anime_context_kb(user_id, store))


def anime_current_payload(
    user_id: str, store: AnimeStore, limit: int
) -> dict[str, object]:
    summary = build_anime_summary(store.items_for_user(user_id), top_limit=limit)
    payload: dict[str, object] = {
        "current": [c.model_dump(mode="json") for c in summary.current]
    }
    return _served(payload, _anime_context_kb(user_id, store))


def anime_history_payload(
    user_id: str, store: AnimeStore, limit: int
) -> dict[str, object]:
    """Lista completa de Anime y manga hasta el límite (D60)."""
    payload: dict[str, object] = {
        "history": items_history(store.items_for_user(user_id), limit=limit)
    }
    return _served(payload, _anime_context_kb(user_id, store))


def _books_context_kb(user_id: str, store: BooksStore) -> float:
    """Tamaño del contexto completo de Libros, referencia de la métrica D28."""
    items = store.items_for_user(user_id)
    summary = build_books_summary(items)
    return _kb(build_books_context(summary, items))


def books_summary_payload(user_id: str, store: BooksStore) -> dict[str, object]:
    summary = build_books_summary(
        store.items_for_user(user_id),
        synced_at=store.status_for_user(user_id).synced_at,
    )
    return _served(summary.model_dump(mode="json"), _books_context_kb(user_id, store))


def books_currently_reading_payload(
    user_id: str, store: BooksStore
) -> dict[str, object]:
    summary = build_books_summary(store.items_for_user(user_id))
    payload: dict[str, object] = {
        "currently_reading": [
            c.model_dump(mode="json") for c in summary.currently_reading
        ]
    }
    return _served(payload, _books_context_kb(user_id, store))


def books_top_authors_payload(
    user_id: str, store: BooksStore, limit: int
) -> dict[str, object]:
    summary = build_books_summary(store.items_for_user(user_id), top_limit=limit)
    payload: dict[str, object] = {
        "top_authors": [a.model_dump(mode="json") for a in summary.top_authors]
    }
    return _served(payload, _books_context_kb(user_id, store))


def books_history_payload(
    user_id: str, store: BooksStore, limit: int
) -> dict[str, object]:
    """Estanterías completas hasta el límite, con metadatos de uso (D60)."""
    payload: dict[str, object] = {
        "history": items_history(store.items_for_user(user_id), limit=limit)
    }
    return _served(payload, _books_context_kb(user_id, store))


# Nombres de tool solo con [a-zA-Z0-9_-]: los clientes de Claude (y otros)
# validan contra ^[a-zA-Z0-9_-]{1,64}$ y rechazan el punto (D63).


@mcp.tool
def ping() -> str:
    """Tool de prueba para verificar la conexión con el servidor MCP."""
    return "pong"


@mcp.tool(name="games_summary")
def games_summary() -> dict[str, object]:
    """Resumen agregado de Juegos: biblioteca, horas, deseados y completado."""
    return games_summary_payload(_require_user(), get_games_store())


@mcp.tool(name="games_top_by_hours")
def games_top_by_hours(limit: int = 10) -> dict[str, object]:
    """Top de juegos por horas jugadas (con completado si está calculado)."""
    return games_top_payload(_require_user(), get_games_store(), limit)


@mcp.tool(name="games_recent")
def games_recent() -> dict[str, object]:
    """Juegos con actividad en las últimas dos semanas."""
    return games_recent_payload(_require_user(), get_games_store())


@mcp.tool(name="games_history")
def games_history(limit: int = MAX_HISTORY_ENTRIES) -> dict[str, object]:
    """Biblioteca completa de Juegos hasta el límite, con metadatos de uso."""
    return games_history_payload(_require_user(), get_games_store(), limit)


@mcp.tool(name="profile_search")
def profile_search(query: str) -> dict[str, object]:
    """Busca una obra por título en el perfil (Juegos, Cine y TV, Anime, Libros)."""
    return profile_search_payload(
        _require_user(),
        get_games_store(),
        get_film_store(),
        get_anime_store(),
        get_books_store(),
        query,
    )


@mcp.tool(name="music_summary")
def music_summary() -> dict[str, object]:
    """Resumen de Música: scrobbles, top artistas y top tracks de la ventana."""
    return music_summary_payload(_require_user(), get_event_store())


@mcp.tool(name="music_top_artists")
def music_top_artists(limit: int = 10) -> dict[str, object]:
    """Artistas más escuchados en los últimos 30 días."""
    return music_top_artists_payload(_require_user(), get_event_store(), limit)


@mcp.tool(name="music_recent")
def music_recent(limit: int = 20) -> dict[str, object]:
    """Últimos listens registrados, del más reciente al más antiguo."""
    return music_recent_payload(_require_user(), get_event_store(), limit)


@mcp.tool(name="music_history")
def music_history(limit: int = MAX_HISTORY_ENTRIES) -> dict[str, object]:
    """Listens completos hasta el límite, del más reciente al más antiguo."""
    return music_history_payload(_require_user(), get_event_store(), limit)


@mcp.tool(name="film_summary")
def film_summary() -> dict[str, object]:
    """Resumen de Cine y TV: películas, series, episodios y horas vistas."""
    return film_summary_payload(_require_user(), get_film_store())


@mcp.tool(name="film_top_movies")
def film_top_movies(limit: int = 10) -> dict[str, object]:
    """Películas más vistas por número de reproducciones."""
    return film_top_movies_payload(_require_user(), get_film_store(), limit)


@mcp.tool(name="film_recent")
def film_recent(limit: int = 10) -> dict[str, object]:
    """Películas y series vistas más recientemente."""
    return film_recent_payload(_require_user(), get_film_store(), limit)


@mcp.tool(name="film_history")
def film_history(limit: int = MAX_HISTORY_ENTRIES) -> dict[str, object]:
    """Historial completo de Cine y TV hasta el límite, con metadatos de uso."""
    return film_history_payload(_require_user(), get_film_store(), limit)


@mcp.tool(name="anime_summary")
def anime_summary() -> dict[str, object]:
    """Resumen de Anime y manga: vistos, leídos, episodios, capítulos y nota media."""
    return anime_summary_payload(_require_user(), get_anime_store())


@mcp.tool(name="anime_top_rated")
def anime_top_rated(limit: int = 10) -> dict[str, object]:
    """Animes y mangas mejor puntuados por el usuario (nota 0-100)."""
    return anime_top_rated_payload(_require_user(), get_anime_store(), limit)


@mcp.tool(name="anime_current")
def anime_current(limit: int = 10) -> dict[str, object]:
    """Animes y mangas en curso (viéndose o leyéndose), con su progreso."""
    return anime_current_payload(_require_user(), get_anime_store(), limit)


@mcp.tool(name="anime_history")
def anime_history(limit: int = MAX_HISTORY_ENTRIES) -> dict[str, object]:
    """Lista completa de Anime y manga hasta el límite, con metadatos de uso."""
    return anime_history_payload(_require_user(), get_anime_store(), limit)


@mcp.tool(name="books_summary")
def books_summary() -> dict[str, object]:
    """Resumen de Libros: leídos, páginas, en curso, por leer y top autores."""
    return books_summary_payload(_require_user(), get_books_store())


@mcp.tool(name="books_currently_reading")
def books_currently_reading() -> dict[str, object]:
    """Libros en curso de lectura."""
    return books_currently_reading_payload(_require_user(), get_books_store())


@mcp.tool(name="books_top_authors")
def books_top_authors(limit: int = 10) -> dict[str, object]:
    """Autores con más libros leídos."""
    return books_top_authors_payload(_require_user(), get_books_store(), limit)


@mcp.tool(name="books_history")
def books_history(limit: int = MAX_HISTORY_ENTRIES) -> dict[str, object]:
    """Estanterías completas de Libros hasta el límite, con metadatos de uso."""
    return books_history_payload(_require_user(), get_books_store(), limit)


@mcp.resource("ethos://games/summary")
def games_summary_resource() -> dict[str, object]:
    """Resource con el resumen de Juegos (misma información que la tool)."""
    return games_summary_payload(_require_user(), get_games_store())


@mcp.resource("ethos://music/summary")
def music_summary_resource() -> dict[str, object]:
    """Resource con el resumen de Música (misma información que la tool)."""
    return music_summary_payload(_require_user(), get_event_store())


@mcp.resource("ethos://film/summary")
def film_summary_resource() -> dict[str, object]:
    """Resource con el resumen de Cine y TV (misma información que la tool)."""
    return film_summary_payload(_require_user(), get_film_store())


@mcp.resource("ethos://anime/summary")
def anime_summary_resource() -> dict[str, object]:
    """Resource con el resumen de Anime y manga (misma información que la tool)."""
    return anime_summary_payload(_require_user(), get_anime_store())


@mcp.resource("ethos://books/summary")
def books_summary_resource() -> dict[str, object]:
    """Resource con el resumen de Libros (misma información que la tool)."""
    return books_summary_payload(_require_user(), get_books_store())
