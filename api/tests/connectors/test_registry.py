"""Tests del registro de conectores y del catálogo de categorías."""

from __future__ import annotations

import pytest

from ethos_api.connectors.listenbrainz.connector import ListenBrainzConnector
from ethos_api.connectors.registry import ConnectorRegistry, registry
from ethos_api.connectors.steam.connector import SteamConnector
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
    assert registry.providers(Category.games) == ["steam"]
    assert registry.providers(Category.music) == ["listenbrainz"]


def test_get_inexistente_lanza_lookup_error() -> None:
    with pytest.raises(LookupError):
        registry.get(Category.film, "trakt")


def test_registro_duplicado_lanza_value_error() -> None:
    limpio = ConnectorRegistry()
    limpio.register(SteamConnector)
    with pytest.raises(ValueError):
        limpio.register(SteamConnector)


def test_providers_de_categoria_sin_conectores() -> None:
    assert registry.providers(Category.books) == []
