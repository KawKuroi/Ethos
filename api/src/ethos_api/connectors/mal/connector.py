"""Conector de MyAnimeList: normaliza las listas al contrato común (D62).

Produce la misma forma que el conector de AniList (D46): `media_type` en
`extra`, progreso en `engagement` y score normalizado 0-100, para que el
resumen y las tools de la categoría funcionen sin cambios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, ItemStatus, NormalizedItem, Work

# Status de MyAnimeList → vocabulario común (mismo mapeo conceptual que D46).
_STATUS_MAP = {
    "completed": ItemStatus.consumed,
    "watching": ItemStatus.in_progress,
    "reading": ItemStatus.in_progress,
    "on_hold": ItemStatus.in_progress,
    "plan_to_watch": ItemStatus.wishlist,
    "plan_to_read": ItemStatus.wishlist,
    "dropped": ItemStatus.abandoned,
}


@dataclass
class MalRawData:
    """Entradas crudas de las listas de anime y manga (API v2)."""

    anime_entries: list[dict[str, Any]] = field(default_factory=list)
    manga_entries: list[dict[str, Any]] = field(default_factory=list)


class MalConnector(Connector[MalRawData, NormalizedItem]):
    """Conector del proveedor MyAnimeList (categoría Anime y manga)."""

    id: ClassVar[str] = "mal"
    category: ClassVar[Category] = Category.anime
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"title", "status", "rating", "engagement", "external_ids"}
    )

    def normalize(self, raw: MalRawData) -> list[NormalizedItem]:
        items: list[NormalizedItem] = []
        for media_type, entries in (
            ("anime", raw.anime_entries),
            ("manga", raw.manga_entries),
        ):
            seen: set[str] = set()
            for entry in entries:
                item = self._normalize_entry(entry, media_type)
                if item is None:
                    continue
                media_id = item.work.external_ids.get("mal", "")
                if media_id in seen:
                    continue
                seen.add(media_id)
                items.append(item)
        return items

    def _normalize_entry(
        self, entry: dict[str, Any], media_type: str
    ) -> NormalizedItem | None:
        node = entry.get("node") or {}
        title = str(node.get("title", "")).strip()
        if not title:
            return None
        list_status = entry.get("list_status") or {}
        status = _STATUS_MAP.get(str(list_status.get("status", "")), ItemStatus.in_library)
        if media_type == "anime":
            progress = int(list_status.get("num_episodes_watched") or 0)
            progress_key = "episodes_progress"
        else:
            progress = int(list_status.get("num_chapters_read") or 0)
            progress_key = "chapters_read"
        engagement = {
            progress_key: progress,
            "repeat": int(list_status.get("num_times_rewatched") or 0)
            or int(list_status.get("num_times_reread") or 0),
        }
        # MAL puntúa 0-10; 0 = sin puntuar. Normalizado a 0-100 como AniList.
        score = int(list_status.get("score") or 0)
        extra: dict[str, object] = {"media_type": media_type}
        node_format = node.get("media_type")
        if node_format:
            extra["format"] = str(node_format).upper()
        updated_at = self._updated_epoch(list_status.get("updated_at"))
        if updated_at:
            extra["updated_at"] = updated_at
        return NormalizedItem(
            work=Work(
                title=title,
                external_ids={"mal": str(node.get("id", ""))},
                extra=extra,
            ),
            category=Category.anime,
            status=status,
            rating_normalized=score * 10 if score > 0 else None,
            rating_original=str(score) if score > 0 else None,
            engagement=engagement,
            source=self.id,
            provenance={"title": self.id, "status": self.id, "engagement": self.id},
        )

    @staticmethod
    def _updated_epoch(value: object) -> int | None:
        # `updated_at` viene como ISO 8601 ("2026-07-01T10:20:30+00:00").
        if not value:
            return None
        try:
            return int(datetime.fromisoformat(str(value)).timestamp())
        except ValueError:
            return None
