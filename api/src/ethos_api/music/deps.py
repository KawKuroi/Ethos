"""Dependencias del slice de música (singletons y factorías inyectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ethos_api.connectors.listenbrainz.client import ListenBrainzClient
from ethos_api.music.service import ListenBrainzApi
from ethos_api.music.store import EventStore, InMemoryEventStore, SupabaseEventStore
from ethos_api.supabase_rest import get_rest

_store: EventStore | None = None


def get_event_store() -> EventStore:
    """Supabase si está configurado; memoria en local/CI (D38)."""
    global _store
    if _store is None:
        rest = get_rest()
        _store = SupabaseEventStore(rest) if rest else InMemoryEventStore()
    return _store


def get_listenbrainz_client() -> ListenBrainzApi:
    """Cliente real de ListenBrainz; los tests lo sustituyen con un fake."""
    return ListenBrainzClient()


EventStoreDep = Annotated[EventStore, Depends(get_event_store)]
ListenBrainzClientDep = Annotated[ListenBrainzApi, Depends(get_listenbrainz_client)]
