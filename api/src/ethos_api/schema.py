"""Contrato de datos normalizado, transversal a todas las categorías.

Modela lo que toda app de tracking describe: una obra y la relación de la
persona con ella, más metadatos de procedencia. Las capas posteriores (MCP,
web, persistencia) consumen este contrato sin depender del conector de origen.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class MediaCategory(StrEnum):
    """Dominio de medios al que pertenece una obra."""

    music = "music"
    film_tv = "film_tv"
    books = "books"
    games = "games"


class ItemStatus(StrEnum):
    """Relación de la persona con la obra (vocabulario común)."""

    in_library = "in_library"
    consumed = "consumed"
    in_progress = "in_progress"
    wishlist = "wishlist"
    abandoned = "abandoned"


class IngestMode(StrEnum):
    """Modo de ingesta de un conector."""

    api = "api"
    import_ = "import"


class Work(BaseModel):
    """Capa específica del dominio: la obra en sí."""

    title: str
    creators: list[str] = Field(default_factory=list)
    year: int | None = None
    # IDs canónicos por dominio (p. ej. {"steam_appid": "440"}). Dan continuidad
    # al cambiar de proveedor y permiten deduplicar dentro de una fuente.
    external_ids: dict[str, str] = Field(default_factory=dict)
    # Campos propios del tipo (plataformas, runtime, páginas, etc.).
    extra: dict[str, object] = Field(default_factory=dict)


class NormalizedItem(BaseModel):
    """Un registro normalizado: la obra, la relación con ella y metadatos."""

    work: Work
    category: MediaCategory
    status: ItemStatus

    # Capa universal de la relación.
    rating_normalized: int | None = Field(default=None, ge=0, le=100)
    rating_original: str | None = None
    favorite: bool = False
    added_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    # Métricas de uso según la fuente (minutos jugados, reproducciones, etc.).
    engagement: dict[str, int] = Field(default_factory=dict)
    review: str | None = None
    tags: list[str] = Field(default_factory=list)

    # Metadatos.
    source: str
    # De qué fuente vino cada campo; alimenta la transparencia del dump.
    provenance: dict[str, str] = Field(default_factory=dict)
    schema_version: int = 1
