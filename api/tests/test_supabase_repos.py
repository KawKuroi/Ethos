"""Tests de los repositorios respaldados por Supabase (PostgREST simulado)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from ethos_api.connectors.steam.connector import SteamProfile
from ethos_api.credentials.models import UserCredential
from ethos_api.credentials.repository import SupabaseCredentialRepository
from ethos_api.games.store import SourceStatus, SupabaseGamesStore, SyncState
from ethos_api.mcp_auth import SupabaseMcpTokenStore
from ethos_api.schema import Category, ItemStatus, NormalizedItem, Work
from ethos_api.supabase_rest import SupabaseRest


class FakePostgrest:
    """Handler de MockTransport que registra peticiones y responde fijo."""

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.requests: list[httpx.Request] = []
        self._responses = responses or {}

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path.rsplit("/", 1)[-1]
        if request.method == "GET":
            return httpx.Response(200, json=self._responses.get(path, []))
        if request.method == "DELETE":
            return httpx.Response(200, json=self._responses.get(f"del:{path}", []))
        return httpx.Response(201, json=[])


def _rest(fake: FakePostgrest) -> SupabaseRest:
    client = httpx.Client(
        transport=httpx.MockTransport(fake), base_url="https://proj.supabase.co/rest/v1"
    )
    return SupabaseRest("https://proj.supabase.co", "service-key", client=client)


def _item(appid: str = "440", minutes: int = 1200) -> NormalizedItem:
    return NormalizedItem(
        work=Work(title="Team Fortress 2", external_ids={"steam_appid": appid}),
        category=Category.games,
        status=ItemStatus.in_library,
        engagement={"playtime_minutes": minutes},
        source="steam",
    )


def test_credenciales_upsert_y_lectura() -> None:
    now = datetime.now(UTC)
    fila = {
        "user_id": "user-1",
        "provider": "steam",
        "category": "games",
        "encrypted_token": "cifrado",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    fake = FakePostgrest({"user_credentials": [fila]})
    repo = SupabaseCredentialRepository(_rest(fake))

    repo.upsert(
        UserCredential(
            user_id="user-1",
            provider="steam",
            category=Category.games,
            encrypted_token="cifrado",
            created_at=now,
            updated_at=now,
        )
    )
    upsert = fake.requests[0]
    assert upsert.method == "POST"
    assert "on_conflict=user_id%2Cprovider" in str(upsert.url)
    assert "merge-duplicates" in upsert.headers["Prefer"]

    encontrada = repo.get("user-1", "steam")
    assert encontrada is not None
    assert encontrada.encrypted_token == "cifrado"


def test_credenciales_delete_reporta_si_borro() -> None:
    fake = FakePostgrest({"del:user_credentials": [{"id": "x"}]})
    repo = SupabaseCredentialRepository(_rest(fake))
    assert repo.delete("user-1", "steam") is True

    vacio = SupabaseCredentialRepository(_rest(FakePostgrest()))
    assert vacio.delete("user-1", "steam") is False


def test_games_store_reemplaza_items() -> None:
    fake = FakePostgrest()
    store = SupabaseGamesStore(_rest(fake))
    store.replace_items("user-1", [_item()])

    # Primero borra lo del usuario/categoría, luego inserta el lote.
    assert fake.requests[0].method == "DELETE"
    assert "user_id=eq.user-1" in str(fake.requests[0].url)
    insert = fake.requests[1]
    assert insert.method == "POST"
    cuerpo = insert.read().decode()
    assert '"external_id": "440"' in cuerpo or '"external_id":"440"' in cuerpo


def test_games_store_lee_items_desde_payload() -> None:
    fake = FakePostgrest(
        {"user_items": [{"payload": _item().model_dump(mode="json")}]}
    )
    store = SupabaseGamesStore(_rest(fake))
    items = store.items_for_user("user-1")
    assert len(items) == 1
    assert items[0].work.title == "Team Fortress 2"


def test_games_store_estado_roundtrip_de_mapeo() -> None:
    synced = datetime(2026, 7, 3, 12, 0, tzinfo=UTC)
    fake = FakePostgrest(
        {
            "source_state": [
                {
                    "status": "synced",
                    "detail": None,
                    "last_synced_at": synced.isoformat(),
                }
            ]
        }
    )
    store = SupabaseGamesStore(_rest(fake))

    store.set_status("user-1", SourceStatus(state=SyncState.fresh, synced_at=synced))
    upsert = fake.requests[0].read().decode()
    assert '"synced"' in upsert  # fresh → synced en la BD

    estado = store.status_for_user("user-1")
    assert estado.state is SyncState.fresh
    assert estado.synced_at == synced


def test_games_store_perfil() -> None:
    fake = FakePostgrest(
        {
            "source_state": [
                {
                    "provider_profile": {
                        "steamid": "765",
                        "persona_name": "Jugador",
                        "avatar_url": None,
                        "visibility": 3,
                    }
                }
            ]
        }
    )
    store = SupabaseGamesStore(_rest(fake))
    store.set_profile(
        "user-1",
        SteamProfile(steamid="765", persona_name="Jugador", avatar_url=None, visibility=3),
    )
    perfil = store.profile_for_user("user-1")
    assert perfil is not None
    assert perfil.persona_name == "Jugador"


def test_event_store_append_y_lectura() -> None:
    from datetime import UTC, datetime

    from ethos_api.music.store import SupabaseEventStore
    from ethos_api.schema import NormalizedEvent

    occurred = datetime(2026, 7, 3, 12, 0, tzinfo=UTC)
    fila = {
        "occurred_at": occurred.isoformat(),
        "payload": {"artist": "Alvvays", "track": "Pharmacist"},
    }
    fake = FakePostgrest({"user_events": [fila]})
    store = SupabaseEventStore(_rest(fake))

    store.append_events(
        "user-1",
        [
            NormalizedEvent(
                category=Category.music,
                occurred_at=occurred,
                payload={"artist": "Alvvays", "track": "Pharmacist"},
                source="listenbrainz",
            )
        ],
    )
    insert = fake.requests[0]
    assert insert.method == "POST"
    assert "user_events" in str(insert.url)

    eventos = store.events_for_user("user-1")
    assert len(eventos) == 1
    assert eventos[0].payload["artist"] == "Alvvays"
    assert store.latest_occurred_at("user-1") == occurred


def test_mcp_tokens_emision_y_resolucion() -> None:
    fake = FakePostgrest({"mcp_tokens": [{"user_id": "user-1"}]})
    store = SupabaseMcpTokenStore(_rest(fake))

    token = store.issue("user-1")
    assert token.startswith("eth_live_")
    upsert = fake.requests[0]
    assert "on_conflict=user_id" in str(upsert.url)
    # Solo viaja el hash, nunca el token en claro.
    assert token not in upsert.read().decode()

    assert store.resolve(token) == "user-1"
    assert store.resolve("sin-prefijo") is None
