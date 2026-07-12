"""Helpers del slice de Anime y manga: datos de muestra y fake de AniList."""

from __future__ import annotations

from typing import Any

from ethos_api.connectors.anilist.client import AniListApiError

# Respuesta de muestra de AniList (misma forma que `data` del GraphQL real).
SAMPLE_MEDIA_LISTS: dict[str, Any] = {
    "anime": {
        "lists": [
            {
                "isCustomList": False,
                "entries": [
                    {
                        "status": "COMPLETED",
                        "score": 90,
                        "progress": 26,
                        "repeat": 1,
                        "updatedAt": 1751500000,
                        "media": {
                            "id": 16498,
                            "title": {
                                "romaji": "Shingeki no Kyojin",
                                "english": "Attack on Titan",
                            },
                            "episodes": 25,
                            "format": "TV",
                        },
                    },
                    {
                        "status": "CURRENT",
                        "score": 0,
                        "progress": 8,
                        "repeat": 0,
                        "updatedAt": 1751600000,
                        "media": {
                            "id": 21,
                            "title": {"romaji": "One Piece"},
                            "episodes": None,
                            "format": "TV",
                        },
                    },
                ],
            },
            {
                # Lista personalizada: repite una obra ya contada (se ignora).
                "isCustomList": True,
                "entries": [
                    {
                        "status": "COMPLETED",
                        "score": 90,
                        "progress": 26,
                        "repeat": 1,
                        "updatedAt": 1751500000,
                        "media": {
                            "id": 16498,
                            "title": {"romaji": "Shingeki no Kyojin"},
                            "episodes": 25,
                            "format": "TV",
                        },
                    },
                ],
            },
        ]
    },
    "manga": {
        "lists": [
            {
                "isCustomList": False,
                "entries": [
                    {
                        "status": "COMPLETED",
                        "score": 100,
                        "progress": 205,
                        "repeat": 0,
                        "updatedAt": 1751400000,
                        "media": {
                            "id": 30013,
                            "title": {"romaji": "Berserk"},
                            "chapters": 380,
                            "format": "MANGA",
                        },
                    },
                    {
                        "status": "PLANNING",
                        "score": 0,
                        "progress": 0,
                        "repeat": 0,
                        "updatedAt": 1751300000,
                        "media": {
                            "id": 30002,
                            "title": {"romaji": "Monster"},
                            "chapters": 162,
                            "format": "MANGA",
                        },
                    },
                ],
            }
        ]
    },
}


class FakeAniListApi:
    """Cliente falso de AniList para los tests del servicio y los endpoints."""

    def __init__(self, *, fail: bool = False, status_code: int | None = None) -> None:
        self.fail = fail
        self.status_code = status_code
        self.calls: list[str] = []

    def get_media_lists(self, user_name: str) -> dict[str, Any]:
        self.calls.append(user_name)
        if self.status_code is not None:
            raise AniListApiError("AniList error", status_code=self.status_code)
        if self.fail:
            raise RuntimeError("AniList respondió 500")
        return SAMPLE_MEDIA_LISTS


class FakeMalApi:
    """Cliente falso de MyAnimeList (una obra por lista)."""

    def __init__(self, *, status_code: int | None = None) -> None:
        self.status_code = status_code

    def _fail_if_needed(self) -> None:
        if self.status_code is not None:
            from ethos_api.connectors.mal.client import MalApiError

            raise MalApiError("MAL error", status_code=self.status_code)

    def get_anime_list(self, user_name: str) -> list[dict[str, Any]]:
        self._fail_if_needed()
        return [
            {
                "node": {"id": 16498, "title": "Shingeki no Kyojin", "media_type": "tv"},
                "list_status": {
                    "status": "completed",
                    "score": 9,
                    "num_episodes_watched": 25,
                },
            }
        ]

    def get_manga_list(self, user_name: str) -> list[dict[str, Any]]:
        self._fail_if_needed()
        return [
            {
                "node": {"id": 2, "title": "Berserk", "media_type": "manga"},
                "list_status": {
                    "status": "completed",
                    "score": 10,
                    "num_chapters_read": 380,
                },
            }
        ]


class FakeKitsuApi:
    """Cliente falso de Kitsu (una obra de anime; manga vacío)."""

    def __init__(self, *, status_code: int | None = None) -> None:
        self.status_code = status_code

    def find_user_id(self, user_name: str) -> str:
        if self.status_code is not None:
            from ethos_api.connectors.kitsu.client import KitsuApiError

            raise KitsuApiError("Kitsu error", status_code=self.status_code)
        return "42"

    def get_library(self, user_id: str, kind: str) -> dict[str, Any]:
        if kind != "anime":
            return {"data": [], "included": []}
        return {
            "data": [
                {
                    "attributes": {
                        "status": "completed",
                        "progress": 25,
                        "ratingTwenty": 18,
                    },
                    "relationships": {
                        "anime": {"data": {"id": "7442", "type": "anime"}}
                    },
                }
            ],
            "included": [
                {
                    "id": "7442",
                    "type": "anime",
                    "attributes": {"canonicalTitle": "Attack on Titan", "subtype": "TV"},
                }
            ],
        }
