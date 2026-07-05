"""Interfaz común de los conectores de fuentes de tracking.

Cada proveedor implementa esta interfaz: declara su identidad y qué campos del
contrato normalizado puede llenar (`capabilities`), y traduce el dato crudo de
la fuente a la salida normalizada mediante `normalize`. La salida es
`NormalizedItem` (fuentes de tipo "obra + relación", p. ej. Steam) o
`NormalizedEvent` (fuentes de tipo evento con timestamp, p. ej. ListenBrainz);
por eso el conector es genérico también en su tipo de salida (D38). Añadir un
proveedor es implementar un conector; nada río abajo cambia.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from ethos_api.schema import Category, IngestMode


class Connector[RawT, OutT](ABC):
    """Contrato que implementa cada proveedor."""

    # Identidad del conector.
    id: ClassVar[str]
    category: ClassVar[Category]
    ingest_mode: ClassVar[IngestMode]
    # Campos del contrato normalizado que esta fuente puede poblar.
    capabilities: ClassVar[frozenset[str]]

    @abstractmethod
    def normalize(self, raw: RawT) -> list[OutT]:
        """Traduce el dato crudo de la fuente a registros normalizados."""
        ...
