"""Registro de conectores: resuelve (categoría, proveedor) → conector (D21).

Las capas río abajo (normalización, persistencia, MCP, web) no conocen
implementaciones concretas: resuelven por este registro. Añadir un proveedor
es implementar su conector y registrarlo aquí; nada más cambia.
"""

from __future__ import annotations

from typing import Any

from ethos_api.connectors.base import Connector
from ethos_api.connectors.listenbrainz.connector import ListenBrainzConnector
from ethos_api.connectors.steam.connector import SteamConnector
from ethos_api.connectors.trakt.connector import TraktConnector
from ethos_api.schema import Category

# El registro guarda clases (los conectores declaran su identidad como
# ClassVars); quien resuelve decide cómo instanciar según sus dependencias.
ConnectorClass = type[Connector[Any, Any]]


class ConnectorRegistry:
    """Asocia cada (categoría, proveedor) con su clase de conector."""

    def __init__(self) -> None:
        self._connectors: dict[tuple[Category, str], ConnectorClass] = {}

    def register(self, connector: ConnectorClass) -> None:
        """Registra un conector por su identidad; rechaza duplicados."""
        key = (connector.category, connector.id)
        if key in self._connectors:
            raise ValueError(
                f"Conector duplicado para {key[0].value}/{key[1]}"
            )
        self._connectors[key] = connector

    def get(self, category: Category, provider: str) -> ConnectorClass:
        """Devuelve la clase del conector registrado para (categoría, proveedor)."""
        try:
            return self._connectors[(category, provider)]
        except KeyError as exc:
            raise LookupError(
                f"No hay conector registrado para {category.value}/{provider}"
            ) from exc

    def providers(self, category: Category) -> list[str]:
        """Proveedores con conector implementado para una categoría."""
        return sorted(pid for (cat, pid) in self._connectors if cat is category)


# Registro por defecto de la aplicación con los conectores implementados.
registry = ConnectorRegistry()
registry.register(SteamConnector)
registry.register(ListenBrainzConnector)
registry.register(TraktConnector)
