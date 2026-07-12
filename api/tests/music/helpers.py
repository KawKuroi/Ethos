"""Helpers del slice de música: fake del cliente de ListenBrainz."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_FIXTURES = Path(__file__).parent.parent / "fixtures"


def load_listens() -> dict[str, Any]:
    """Fixture estática (timestamps fijos) para los tests del conector/resumen."""
    return json.loads((_FIXTURES / "listenbrainz_listens.json").read_text(encoding="utf-8"))


class FakeListenBrainzApi:
    """Cliente falso con listens **recientes** (caen en la ventana de 30 días).

    Genera un conjunto fijo al construirse (Alvvays x2, Mitski x1 y uno vacío
    que se descarta) y respeta `min_ts` para el refresco incremental.
    """

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[int | None] = []
        now = int(datetime.now(UTC).timestamp())
        self.latest = now - 60
        self._listens: list[dict[str, Any]] = [
            {
                "listened_at": now - 60,
                "track_metadata": {
                    "artist_name": "Alvvays",
                    "track_name": "Belinda Says",
                    "release_name": "Blue Rev",
                },
            },
            {
                "listened_at": now - 120,
                "track_metadata": {
                    "artist_name": "Alvvays",
                    "track_name": "Pharmacist",
                    "release_name": "Blue Rev",
                },
            },
            {
                "listened_at": now - 180,
                "track_metadata": {
                    "artist_name": "Mitski",
                    "track_name": "My Love Mine All Mine",
                },
            },
            {
                "listened_at": now - 240,
                "track_metadata": {"artist_name": "", "track_name": ""},
            },
        ]

    def get_listens(
        self, user_name: str, *, min_ts: int | None = None, count: int = 100
    ) -> dict[str, Any]:
        self.calls.append(min_ts)
        if self.fail:
            raise RuntimeError("ListenBrainz respondió 500")
        listens = self._listens
        if min_ts is not None:
            listens = [x for x in listens if int(x["listened_at"]) > min_ts]
        return {"payload": {"count": len(listens), "listens": listens}}


class FakeLastfmApi:
    """Cliente falso de Last.fm con scrobbles recientes (ventana de 30 días)."""

    def __init__(self, *, status_code: int | None = None) -> None:
        self.status_code = status_code
        self.calls: list[int | None] = []
        now = int(datetime.now(UTC).timestamp())
        self._tracks: list[dict[str, Any]] = [
            {
                "name": "Belinda Says",
                "artist": {"#text": "Alvvays"},
                "album": {"#text": "Blue Rev"},
                "date": {"uts": str(now - 60)},
            },
            {
                "name": "Star",
                "artist": {"#text": "Mitski"},
                "album": {"#text": ""},
                "date": {"uts": str(now - 120)},
            },
        ]

    def get_recent_tracks(
        self,
        user_name: str,
        *,
        from_ts: int | None = None,
        page: int = 1,
        limit: int = 200,
    ) -> dict[str, Any]:
        from ethos_api.connectors.lastfm.client import LastfmApiError

        self.calls.append(from_ts)
        if self.status_code is not None:
            raise LastfmApiError("Last.fm error", status_code=self.status_code)
        tracks = self._tracks
        if from_ts is not None:
            tracks = [t for t in tracks if int(t["date"]["uts"]) > from_ts]
        return {"recenttracks": {"track": tracks, "@attr": {"page": "1"}}}
