"""Tests de la verificación OpenID de Steam (sin red, con MockTransport)."""

from __future__ import annotations

import httpx
import pytest

from ethos_api.connectors.steam.openid import (
    STEAM_OPENID_URL,
    SteamOpenIdError,
    build_login_url,
    verify_openid_response,
)

_STEAMID = "76561197960287930"


def _params(**overrides: str) -> dict[str, str]:
    base = {
        "openid.mode": "id_res",
        "openid.op_endpoint": STEAM_OPENID_URL,
        "openid.claimed_id": f"https://steamcommunity.com/openid/id/{_STEAMID}",
        "openid.identity": f"https://steamcommunity.com/openid/id/{_STEAMID}",
        "openid.return_to": "https://ethos-steel.vercel.app/app/fuentes",
        "openid.response_nonce": "2026-07-03T00:00:00Znonce",
        "openid.assoc_handle": "1234",
        "openid.signed": (
            "signed,op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle"
        ),
        "openid.sig": "firma",
    }
    base.update(overrides)
    return base


def _client(body: str, status_code: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert b"check_authentication" in request.read()
        return httpx.Response(status_code, text=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_verifica_y_devuelve_steamid() -> None:
    client = _client("ns:http://specs.openid.net/auth/2.0\nis_valid:true\n")
    assert verify_openid_response(_params(), client=client) == _STEAMID


def test_rechaza_firma_invalida() -> None:
    client = _client("ns:http://specs.openid.net/auth/2.0\nis_valid:false\n")
    with pytest.raises(SteamOpenIdError):
        verify_openid_response(_params(), client=client)


def test_rechaza_modo_incorrecto() -> None:
    with pytest.raises(SteamOpenIdError):
        verify_openid_response(_params(**{"openid.mode": "cancel"}))


def test_rechaza_op_endpoint_ajeno() -> None:
    with pytest.raises(SteamOpenIdError):
        verify_openid_response(
            _params(**{"openid.op_endpoint": "https://atacante.example/openid"})
        )


def test_rechaza_firma_sin_campos_obligatorios() -> None:
    with pytest.raises(SteamOpenIdError):
        verify_openid_response(_params(**{"openid.signed": "signed,assoc_handle"}))


def test_rechaza_claimed_id_que_no_es_steam() -> None:
    with pytest.raises(SteamOpenIdError):
        verify_openid_response(
            _params(**{"openid.claimed_id": "https://atacante.example/id/1"})
        )


def test_build_login_url() -> None:
    url = build_login_url(
        "https://ethos-steel.vercel.app/app/fuentes", "https://ethos-steel.vercel.app"
    )
    assert url.startswith(STEAM_OPENID_URL)
    assert "checkid_setup" in url
    assert "identifier_select" in url
