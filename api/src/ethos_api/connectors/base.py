"""Interfaz común de los conectores de fuentes de tracking.

Cada proveedor implementa esta interfaz: declara su identidad y qué campos del
contrato normalizado puede llenar (`capabilities`), y traduce el dato crudo de
la fuente a `NormalizedItem` mediante `normalize`. Añadir un proveedor es
implementar un conector; nada río abajo cambia.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from ethos_api.schema import IngestMode, MediaCategory, NormalizedItem


class Connector[RawT](ABC):
    """Contrato que implementa cada proveedor."""

    # Identidad del conector.
    id: ClassVar[str]
    category: ClassVar[MediaCategory]
    ingest_mode: ClassVar[IngestMode]
    # Campos del contrato normalizado que esta fuente puede poblar.
    capabilities: ClassVar[frozenset[str]]

    @abstractmethod
    def normalize(self, raw: RawT) -> list[NormalizedItem]:
        """Traduce el dato crudo de la fuente a registros normalizados."""
        ...
