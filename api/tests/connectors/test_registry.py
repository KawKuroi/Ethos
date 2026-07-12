"""Tests del registro de conectores y del catálogo de categorías."""

from __future__ import annotations

import pytest

from ethos_api.connectors.anilist.connector import AniListConnector
from ethos_api.connectors.goodreads.connector import GoodreadsConnector
from ethos_api.connectors.listenbrainz.connector import ListenBrainzConnector
from ethos_api.connectors.registry import ConnectorRegistry, registry
from ethos_api.connectors.steam.connector import SteamConnector
from ethos_api.connectors.trakt.connector import TraktConnector
from ethos_api.schema import Category


def test_catalogo_de_5_categorias() -> None:
    # Los valores son los ids del diseño; catálogo activo de D27 (D31 retira fitness).
    assert [c.value for c in Category] == [
        "games",
        "music",
        "film",
        "anime",
        "books",
    ]


def test_registro_por_defecto_resuelve_conectores() -> None:
    assert registry.get(Category.games, "steam") is SteamConnector
    assert registry.get(Category.music, "listenbrainz") is ListenBrainzConnector
    assert registry.get(Category.film, "trakt") is TraktConnector
    assert registry.get(Category.anime, "anilist") is AniListConnector
    assert registry.get(Category.books, "goodreads") is GoodreadsConnector
    # Catálogo de proveedores alternativos integrado (D62).
    assert registry.providers(Category.games) == ["steam"]
    assert registry.providers(Category.music) == [
        "applemusic",
        "lastfm",
        "listenbrainz",
        "spotify",
    ]
    assert registry.providers(Category.film) == ["imdb", "letterboxd", "trakt"]
    assert registry.providers(Category.anime) == ["anilist", "kitsu", "mal"]
    assert registry.providers(Category.books) == [
        "goodreads",
        "hardcover",
        "openlibrary",
        "storygraph",
    ]


def test_get_inexistente_lanza_lookup_error() -> None:
    with pytest.raises(LookupError):
        registry.get(Category.games, "gog")


def test_registro_duplicado_lanza_value_error() -> None:
    limpio = ConnectorRegistry()
    limpio.register(SteamConnector)
    with pytest.raises(ValueError):
        limpio.register(SteamConnector)


def test_todas_las_categorias_tienen_conector() -> None:
    # Con la Fase 3 completa, ninguna categoría del catálogo queda sin proveedor.
    for category in Category:
        assert registry.providers(category), category.value
