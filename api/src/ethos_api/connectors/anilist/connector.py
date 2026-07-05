"""Conector de AniList: normaliza las listas de anime y manga al contrato común."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Status de AniList → vocabulario común (D46).
_STATUS_MAP = {
    "COMPLETED": ItemStatus.consumed,
    "CURRENT": ItemStatus.in_progress,
    "REPEATING": ItemStatus.in_progress,
    "PAUSED": ItemStatus.in_progress,
    "PLANNING": ItemStatus.wishlist,
    "DROPPED": ItemStatus.abandoned,
}


@dataclass
class AniListRawData:
    """Colecciones crudas de AniList para un usuario (`MediaListCollection`)."""

    anime_lists: list[dict[str, Any]] = field(default_factory=list)
    manga_lists: list[dict[str, Any]] = field(default_factory=list)


class AniListConnector(Connector[AniListRawData, NormalizedItem]):
    """Conector del proveedor AniList (categoría Anime y manga)."""

    id: ClassVar[str] = "anilist"
    category: ClassVar[Category] = Category.anime
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "rating", "engagement", "external_ids"}
    )

    def normalize(self, raw: AniListRawData) -> list[NormalizedItem]:
        items: list[NormalizedItem] = []
        # Una obra puede repetirse entre la lista estándar y las personalizadas;
        # se deduplica por id de AniList dentro de cada tipo.
        for media_type, lists in (("anime", raw.anime_lists), ("manga", raw.manga_lists)):
            seen: set[str] = set()
            for media_list in lists:
                if media_list.get("isCustomList"):
                    continue
                for entry in media_list.get("entries", []):
                    item = self._normalize_entry(entry, media_type)
                    if item is None:
                        continue
                    media_id = item.work.external_ids.get("anilist", "")
                    if media_id in seen:
                        continue
                    seen.add(media_id)
                    items.append(item)
        return items

    def _normalize_entry(
        self, entry: dict[str, Any], media_type: str
    ) -> NormalizedItem | None:
        media = entry.get("media") or {}
        title = self._title(media)
        if not title:
            return None
        status = _STATUS_MAP.get(str(entry.get("status", "")), ItemStatus.in_library)
        progress = int(entry.get("progress") or 0)
        engagement = {
            "episodes_progress" if media_type == "anime" else "chapters_read": progress,
            "repeat": int(entry.get("repeat") or 0),
        }
        # AniList devuelve score 0 cuando la obra no está puntuada.
        score = int(entry.get("score") or 0)
        extra: dict[str, object] = {"media_type": media_type}
        media_format = media.get("format")
        if media_format:
            extra["format"] = str(media_format)
        updated_at = entry.get("updatedAt")
        if updated_at:
            extra["updated_at"] = int(updated_at)
        return NormalizedItem(
            work=Work(
                title=title,
                external_ids={"anilist": str(media.get("id", ""))},
                extra=extra,
            ),
            category=Category.anime,
            status=status,
            rating_normalized=score if score > 0 else None,
            engagement=engagement,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "engagement": self.id},
        )

    @staticmethod
    def _title(media: dict[str, Any]) -> str:
        titles = media.get("title") or {}
        return str(titles.get("romaji") or titles.get("english") or "")
