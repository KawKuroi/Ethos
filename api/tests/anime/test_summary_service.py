"""Tests del resumen y del servicio de refresco de Anime y manga."""

from __future__ import annotations

from ethos_api.anime.service import refresh_user_anime
from ethos_api.anime.store import InMemoryAnimeStore
from ethos_api.anime.summary import build_anime_summary
from ethos_api.connectors.anilist.connector import AniListConnector, AniListRawData
from ethos_api.sources_status import SyncState
from tests.anime.helpers import SAMPLE_MEDIA_LISTS, FakeAniListApi


def _items() -> list:
    raw = AniListRawData(
        anime_lists=SAMPLE_MEDIA_LISTS["anime"]["lists"],
        manga_lists=SAMPLE_MEDIA_LISTS["manga"]["lists"],
    )
    return AniListConnector().normalize(raw)


def test_resumen_agrega_conteos_y_nota_media() -> None:
    summary = build_anime_summary(_items())
    assert summary.anime_watched == 1
    assert summary.manga_read == 1
    assert summary.episodes_watched == 34  # 26 + 8 en curso
    assert summary.chapters_read == 205
    assert summary.mean_score == 95.0
    assert summary.top_rated[0].title == "Berserk"
    assert summary.top_rated[0].score == 100
    assert [c.title for c in summary.current] == ["One Piece"]


def test_resumen_vacio_no_rompe() -> None:
    summary = build_anime_summary([])
    assert summary.anime_watched == 0
    assert summary.mean_score is None
    assert summary.top_rated == []
    assert summary.current == []


def test_refresco_puebla_store_y_estado() -> None:
    store = InMemoryAnimeStore()
    refresh_user_anime("user-1", "otaku", FakeAniListApi(), store)
    assert len(store.items_for_user("user-1")) == 4
    status = store.status_for_user("user-1")
    assert status.state is SyncState.fresh
    assert status.synced_at is not None


def test_usuario_privado_o_inexistente_deja_estado_private() -> None:
    store = InMemoryAnimeStore()
    refresh_user_anime("user-1", "privado", FakeAniListApi(status_code=404), store)
    status = store.status_for_user("user-1")
    assert status.state is SyncState.private
    assert status.detail is not None
    assert store.items_for_user("user-1") == []


def test_error_generico_deja_estado_error() -> None:
    store = InMemoryAnimeStore()
    refresh_user_anime("user-1", "otaku", FakeAniListApi(fail=True), store)
    assert store.status_for_user("user-1").state is SyncState.error
