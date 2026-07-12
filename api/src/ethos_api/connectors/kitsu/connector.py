"""Conector de Kitsu: normaliza library entries al contrato común (D62).

Produce la misma forma que AniList/MAL: `media_type` en `extra`, progreso en
`engagement` y score 0-100 (Kitsu puntúa `ratingTwenty` 2-20, por 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Status de Kitsu → vocabulario común.
_STATUS_MAP = {
    "completed": ItemStatus.consumed,
    "current": ItemStatus.in_progress,
    "on_hold": ItemStatus.in_progress,
    "planned": ItemStatus.wishlist,
    "dropped": ItemStatus.abandoned,
}


@dataclass
class KitsuRawData:
    """Library entries crudas (JSON:API) con las obras en `included`."""

    anime_library: dict[str, Any] = field(default_factory=dict)
    manga_library: dict[str, Any] = field(default_factory=dict)


class KitsuConnector(Connector[KitsuRawData, NormalizedItem]):
    """Conector del proveedor Kitsu (categoría Anime y manga)."""

    id: ClassVar[str] = "kitsu"
    category: ClassVar[Category] = Category.anime
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "rating", "engagement", "external_ids"}
    )

    def normalize(self, raw: KitsuRawData) -> list[NormalizedItem]:
        items: list[NormalizedItem] = []
        for media_type, library in (
            ("anime", raw.anime_library),
            ("manga", raw.manga_library),
        ):
            media_by_id = {
                str(media.get("id", "")): media
                for media in library.get("included", [])
                if media.get("type") == media_type
            }
            seen: set[str] = set()
            for entry in library.get("data", []):
                item = self._normalize_entry(entry, media_by_id, media_type)
                if item is None:
                    continue
                media_id = item.work.external_ids.get("kitsu", "")
                if media_id in seen:
                    continue
                seen.add(media_id)
                items.append(item)
        return items

    def _normalize_entry(
        self,
        entry: dict[str, Any],
        media_by_id: dict[str, dict[str, Any]],
        media_type: str,
    ) -> NormalizedItem | None:
        relationships = entry.get("relationships") or {}
        media_ref = (relationships.get(media_type) or {}).get("data") or {}
        media = media_by_id.get(str(media_ref.get("id", "")))
        if media is None:
            return None
        media_attrs = media.get("attributes") or {}
        title = str(media_attrs.get("canonicalTitle", "")).strip()
        if not title:
            return None
        attrs = entry.get("attributes") or {}
        status = _STATUS_MAP.get(str(attrs.get("status", "")), ItemStatus.in_library)
        progress = int(attrs.get("progress") or 0)
        engagement = {
            "episodes_progress" if media_type == "anime" else "chapters_read": progress,
            "repeat": int(attrs.get("reconsumeCount") or 0),
        }
        # ratingTwenty va de 2 a 20; None = sin puntuar. Normalizado a 0-100.
        rating_twenty = attrs.get("ratingTwenty")
        rating = int(rating_twenty) * 5 if rating_twenty else None
        extra: dict[str, object] = {"media_type": media_type}
        subtype = media_attrs.get("subtype")
        if subtype:
            extra["format"] = str(subtype).upper()
        updated_at = self._updated_epoch(attrs.get("updatedAt"))
        if updated_at:
            extra["updated_at"] = updated_at
        return NormalizedItem(
            work=Work(
                title=title,
                external_ids={"kitsu": str(media.get("id", ""))},
                extra=extra,
            ),
            category=Category.anime,
            status=status,
            rating_normalized=rating,
            rating_original=str(rating_twenty) if rating_twenty else None,
            engagement=engagement,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "engagement": self.id},
        )

    @staticmethod
    def _updated_epoch(value: object) -> int | None:
        # `updatedAt` viene como ISO 8601 con Z ("2026-07-01T10:20:30.000Z").
        if not value:
            return None
        try:
            return int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp())
        except ValueError:
            return None
