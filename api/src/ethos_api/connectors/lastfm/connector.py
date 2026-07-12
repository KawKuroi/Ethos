"""Conector de Last.fm: normaliza scrobbles a eventos con timestamp (D62)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from ethos_api.connectors.base import Connector
from ethos_api.schema import Category, IngestMode, NormalizedEvent


@dataclass
class LastfmRawData:
    """Respuesta cruda de `user.getRecentTracks` (una o varias páginas)."""

    pages: list[dict[str, Any]]


class LastfmConnector(Connector[LastfmRawData, NormalizedEvent]):
    """Conector del proveedor Last.fm (categoría Música, API)."""

    id: ClassVar[str] = "lastfm"
    category: ClassVar[Category] = Category.music
    ingest_mode: ClassVar[IngestMode] = IngestMode.api
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"artist", "track", "release", "occurred_at"}
    )

    def normalize(self, raw: LastfmRawData) -> list[NormalizedEvent]:
        events: list[NormalizedEvent] = []
        for page in raw.pages:
            tracks = page.get("recenttracks", {}).get("track", [])
            # Con un solo scrobble la API devuelve un objeto, no una lista.
            if isinstance(tracks, dict):
                tracks = [tracks]
            for track in tracks:
                event = self._normalize_track(track)
                if event is not None:
                    events.append(event)
        return events

    def _normalize_track(self, track: dict[str, Any]) -> NormalizedEvent | None:
        # El track "now playing" no tiene fecha: no es un scrobble cerrado.
        if track.get("@attr", {}).get("nowplaying"):
            return None
        uts = track.get("date", {}).get("uts")
        name = str(track.get("name", "")).strip()
        artist = str(track.get("artist", {}).get("#text", "")).strip()
        if not uts or not name or not artist:
            return None
        payload = {"artist": artist, "track": name}
        release = str(track.get("album", {}).get("#text", "")).strip()
        if release:
            payload["release"] = release
        return NormalizedEvent(
            category=Category.music,
            occurred_at=datetime.fromtimestamp(int(uts), tz=UTC),
            payload=payload,
            source=self.id,
        )

    @staticmethod
    def latest_scrobbled_at(raw: LastfmRawData) -> int | None:
        """Mayor `uts` de la respuesta (llave del refresco incremental)."""
        stamps: list[int] = []
        for page in raw.pages:
            tracks = page.get("recenttracks", {}).get("track", [])
            if isinstance(tracks, dict):
                tracks = [tracks]
            stamps.extend(
                int(track["date"]["uts"])
                for track in tracks
                if track.get("date", {}).get("uts")
            )
        return max(stamps) if stamps else None
