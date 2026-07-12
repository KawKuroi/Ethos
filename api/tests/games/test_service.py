"""Tests del refresco de la fuente de juegos (D33/D36)."""

from __future__ import annotations

from ethos_api.connectors.steam.connector import SteamProfile
from ethos_api.games.service import refresh_user_games
from ethos_api.games.store import InMemoryGamesStore, SyncState
from ethos_api.schema import ItemStatus, NormalizedItem
from tests.games.helpers import FakeSteamApi


def test_refresco_persiste_items_perfil_y_estado_fresh() -> None:
    store = InMemoryGamesStore()
    client = FakeSteamApi()

    refresh_user_games("user-1", "765", client, store)

    status = store.status_for_user("user-1")
    assert status.state is SyncState.fresh
    assert status.synced_at is not None

    items = store.items_for_user("user-1")
    library = [i for i in items if i.status is ItemStatus.in_library]
    wishlist = [i for i in items if i.status is ItemStatus.wishlist]
    assert len(library) == 2
    assert len(wishlist) == 3

    profile = store.profile_for_user("user-1")
    assert profile is not None
    assert profile.persona_name == "Jugador"

    # Completado dentro del presupuesto: una llamada por juego de la biblioteca.
    assert sorted(client.achievement_calls) == [440, 570]
    tf2 = store.item_by_appid("user-1", "440")
    assert tf2 is not None
    assert tf2.work.extra["completion_pct"] == 75.0

    # Géneros enriquecidos desde la store, mismo presupuesto (D55).
    assert sorted(client.genre_calls) == [440, 570]
    assert tf2.work.extra["genres"] == ["Acción", "Indie"]


def test_el_perfil_se_persiste_despues_de_los_items() -> None:
    """Regresión: el perfil guardado al empezar el refresco hacía que
    /sources/games devolviera un resumen "parcial" con todo a cero durante la
    primera sincronización, y la web lo pintaba como si ya hubiera datos."""

    class RecordingStore(InMemoryGamesStore):
        def __init__(self) -> None:
            super().__init__()
            self.events: list[str] = []

        def set_profile(self, user_id: str, profile: SteamProfile) -> None:
            self.events.append("profile")
            super().set_profile(user_id, profile)

        def replace_items(self, user_id: str, items: list[NormalizedItem]) -> None:
            self.events.append("items")
            super().replace_items(user_id, items)

    store = RecordingStore()
    refresh_user_games("user-1", "765", FakeSteamApi(), store)

    assert store.events == ["items", "profile"]
    assert store.status_for_user("user-1").state is SyncState.fresh


def test_perfil_privado_deja_estado_private_sin_items() -> None:
    store = InMemoryGamesStore()
    refresh_user_games("user-1", "765", FakeSteamApi(visibility=1), store)

    status = store.status_for_user("user-1")
    assert status.state is SyncState.private
    assert store.items_for_user("user-1") == []
    # No se gastan llamadas de logros con el perfil privado.


def test_error_de_steam_deja_estado_error() -> None:
    store = InMemoryGamesStore()
    refresh_user_games("user-1", "765", FakeSteamApi(fail_owned=True), store)

    status = store.status_for_user("user-1")
    assert status.state is SyncState.error
    assert status.detail is not None


def test_fallo_de_logros_no_tumba_el_refresco() -> None:
    store = InMemoryGamesStore()
    refresh_user_games("user-1", "765", FakeSteamApi(fail_achievements=True), store)

    assert store.status_for_user("user-1").state is SyncState.fresh
    tf2 = store.item_by_appid("user-1", "440")
    assert tf2 is not None
    assert "completion_pct" not in tf2.work.extra


def test_fallo_de_generos_no_tumba_el_refresco() -> None:
    store = InMemoryGamesStore()
    refresh_user_games("user-1", "765", FakeSteamApi(fail_genres=True), store)

    assert store.status_for_user("user-1").state is SyncState.fresh
    tf2 = store.item_by_appid("user-1", "440")
    assert tf2 is not None
    assert "genres" not in tf2.work.extra
