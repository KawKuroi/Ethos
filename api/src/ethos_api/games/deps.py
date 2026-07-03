"""Dependencias del slice de juegos (singletons y factorías inyectables)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from ethos_api.config import settings
from ethos_api.connectors.steam.client import SteamApiClient
from ethos_api.connectors.steam.openid import verify_openid_response
from ethos_api.games.service import SteamGamesApi
from ethos_api.games.store import GamesStore, InMemoryGamesStore

_store: GamesStore = InMemoryGamesStore()


def get_games_store() -> GamesStore:
    return _store


def get_steam_client() -> SteamGamesApi:
    """Cliente real de Steam; los tests lo sustituyen con un fake."""
    return SteamApiClient(settings.steam_api_key.get_secret_value())


def get_openid_verifier() -> Callable[[dict[str, str]], str]:
    """Verificador OpenID; los tests lo sustituyen sin tocar la red."""
    return verify_openid_response


GamesStoreDep = Annotated[GamesStore, Depends(get_games_store)]
SteamClientDep = Annotated[SteamGamesApi, Depends(get_steam_client)]
OpenIdVerifierDep = Annotated[Callable[[dict[str, str]], str], Depends(get_openid_verifier)]
