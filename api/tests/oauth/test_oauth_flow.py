"""Tests del flujo OAuth 2.1 del MCP (D56): DCR + PKCE + tokens + discovery."""

from __future__ import annotations

import base64
import hashlib
import secrets
from collections.abc import Iterator
from urllib.parse import parse_qs, quote, urlparse

import pytest
from fastapi.testclient import TestClient

from ethos_api.main import app
from ethos_api.mcp_auth import resolve_bearer_user
from ethos_api.oauth import deps
from ethos_api.oauth.store import (
    InMemoryCodeStore,
    InMemoryOAuthClientStore,
    InMemoryOAuthTokenStore,
)
from tests.helpers import auth_headers

REDIRECT = "https://client.example/callback"


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


@pytest.fixture
def client(
    jwt_secret: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[TestClient, InMemoryOAuthTokenStore]]:
    # Se parchean los singletons del módulo (no la DI): el middleware del
    # desafío 401 resuelve tokens fuera del ciclo de dependencias de FastAPI.
    monkeypatch.setattr(deps, "_clients", InMemoryOAuthClientStore())
    tokens = InMemoryOAuthTokenStore()
    monkeypatch.setattr(deps, "_tokens", tokens)
    monkeypatch.setattr(deps, "_codes", InMemoryCodeStore())
    with TestClient(app) as test_client:
        yield test_client, tokens


def _register(test_client: TestClient) -> str:
    respuesta = test_client.post(
        "/oauth/register",
        json={"client_name": "Claude", "redirect_uris": [REDIRECT]},
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["token_endpoint_auth_method"] == "none"
    return str(datos["client_id"])


def _authorize_and_approve(
    test_client: TestClient, client_id: str, challenge: str
) -> str:
    """Recorre authorize (redirect al consentimiento) + approve; devuelve el code."""
    respuesta = test_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": "abc",
        },
        follow_redirects=False,
    )
    assert respuesta.status_code == 307
    consent = urlparse(respuesta.headers["location"])
    assert consent.path == "/oauth/autorizar"

    aprobacion = test_client.post(
        "/oauth/approve",
        json={
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "code_challenge": challenge,
            "state": "abc",
            "approve": True,
        },
        headers=auth_headers("user-1"),
    )
    assert aprobacion.status_code == 200
    destino = urlparse(aprobacion.json()["redirect_to"])
    params = parse_qs(destino.query)
    assert params["state"] == ["abc"]
    return params["code"][0]


def test_flujo_completo_emite_token_valido_para_el_mcp(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, tokens = client
    verifier, challenge = _pkce()
    client_id = _register(test_client)
    code = _authorize_and_approve(test_client, client_id, challenge)

    respuesta = test_client.post(
        "/oauth/token",
        content=(
            f"grant_type=authorization_code&code={code}&client_id={client_id}"
            f"&redirect_uri={REDIRECT}&code_verifier={verifier}"
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["token_type"] == "Bearer"
    assert datos["access_token"].startswith("eth_oauth_")
    assert datos["refresh_token"].startswith("eth_refresh_")
    assert datos["expires_in"] > 0

    # El access token resuelve al usuario que aprobó.
    assert tokens.resolve_access(datos["access_token"]) == "user-1"


def test_verifier_incorrecto_rechazado(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    _, challenge = _pkce()
    client_id = _register(test_client)
    code = _authorize_and_approve(test_client, client_id, challenge)

    respuesta = test_client.post(
        "/oauth/token",
        content=(
            f"grant_type=authorization_code&code={code}&client_id={client_id}"
            f"&redirect_uri={REDIRECT}&code_verifier=verificador-equivocado"
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["error"] == "invalid_grant"


def test_code_es_de_un_solo_uso(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    verifier, challenge = _pkce()
    client_id = _register(test_client)
    code = _authorize_and_approve(test_client, client_id, challenge)

    body = (
        f"grant_type=authorization_code&code={code}&client_id={client_id}"
        f"&redirect_uri={REDIRECT}&code_verifier={verifier}"
    )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    assert test_client.post("/oauth/token", content=body, headers=headers).status_code == 200
    segundo = test_client.post("/oauth/token", content=body, headers=headers)
    assert segundo.status_code == 400
    assert segundo.json()["error"] == "invalid_grant"


def test_refresh_rota_el_token(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, tokens = client
    verifier, challenge = _pkce()
    client_id = _register(test_client)
    code = _authorize_and_approve(test_client, client_id, challenge)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    primero = test_client.post(
        "/oauth/token",
        content=(
            f"grant_type=authorization_code&code={code}&client_id={client_id}"
            f"&redirect_uri={REDIRECT}&code_verifier={verifier}"
        ),
        headers=headers,
    ).json()

    segundo = test_client.post(
        "/oauth/token",
        content=f"grant_type=refresh_token&refresh_token={primero['refresh_token']}",
        headers=headers,
    )
    assert segundo.status_code == 200
    assert tokens.resolve_access(segundo.json()["access_token"]) == "user-1"

    # El refresh usado quedó invalidado (rotación).
    tercero = test_client.post(
        "/oauth/token",
        content=f"grant_type=refresh_token&refresh_token={primero['refresh_token']}",
        headers=headers,
    )
    assert tercero.status_code == 400


def test_denegar_devuelve_access_denied(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    _, challenge = _pkce()
    client_id = _register(test_client)
    respuesta = test_client.post(
        "/oauth/approve",
        json={
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "code_challenge": challenge,
            "state": "xyz",
            "approve": False,
        },
        headers=auth_headers(),
    )
    destino = parse_qs(urlparse(respuesta.json()["redirect_to"]).query)
    assert destino["error"] == ["access_denied"]
    assert destino["state"] == ["xyz"]


def test_redirect_uri_no_registrada_es_400_sin_redireccion(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    _, challenge = _pkce()
    client_id = _register(test_client)
    respuesta = test_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": "https://atacante.example/callback",
            "code_challenge": challenge,
        },
        follow_redirects=False,
    )
    assert respuesta.status_code == 400


def test_registro_rechaza_redirects_no_seguras(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.post(
        "/oauth/register",
        json={"client_name": "Malo", "redirect_uris": ["http://atacante.example/cb"]},
    )
    assert respuesta.status_code == 400


def test_discovery_metadata(client: tuple[TestClient, InMemoryOAuthTokenStore]) -> None:
    test_client, _ = client
    auth_server = test_client.get("/.well-known/oauth-authorization-server").json()
    assert auth_server["code_challenge_methods_supported"] == ["S256"]
    assert auth_server["authorization_endpoint"].endswith("/oauth/authorize")
    assert auth_server["revocation_endpoint"].endswith("/oauth/revoke")
    assert "offline_access" in auth_server["scopes_supported"]

    recurso = test_client.get("/.well-known/oauth-protected-resource/mcp").json()
    assert recurso["resource"].endswith("/mcp/")
    assert recurso["authorization_servers"] == [auth_server["issuer"]]

    # Aliases que prueban los clientes MCP como fallback de discovery.
    for alias in (
        "/.well-known/oauth-authorization-server/mcp",
        "/.well-known/openid-configuration",
    ):
        assert test_client.get(alias).json()["issuer"] == auth_server["issuer"]


def test_redirect_loopback_acepta_cualquier_puerto(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    """RFC 8252 §7.3: los clientes nativos abren un puerto efímero por sesión."""
    test_client, _ = client
    verifier, challenge = _pkce()
    respuesta = test_client.post(
        "/oauth/register",
        json={
            "client_name": "Claude Code",
            "redirect_uris": ["http://localhost/callback", "http://127.0.0.1/callback"],
        },
    )
    assert respuesta.status_code == 201
    client_id = str(respuesta.json()["client_id"])
    ported = "http://localhost:53211/callback"

    autorizacion = test_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": ported,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
        follow_redirects=False,
    )
    assert autorizacion.status_code == 307

    aprobacion = test_client.post(
        "/oauth/approve",
        json={
            "client_id": client_id,
            "redirect_uri": ported,
            "code_challenge": challenge,
            "approve": True,
        },
        headers=auth_headers("user-1"),
    )
    assert aprobacion.status_code == 200
    code = parse_qs(urlparse(aprobacion.json()["redirect_to"]).query)["code"][0]

    canje = test_client.post(
        "/oauth/token",
        content=(
            f"grant_type=authorization_code&code={code}&client_id={client_id}"
            f"&redirect_uri={quote(ported, safe='')}&code_verifier={verifier}"
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert canje.status_code == 200


def test_redirect_loopback_con_otro_path_rechazada(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    _, challenge = _pkce()
    respuesta = test_client.post(
        "/oauth/register",
        json={"client_name": "Nativo", "redirect_uris": ["http://localhost/callback"]},
    )
    client_id = str(respuesta.json()["client_id"])
    autorizacion = test_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": "http://localhost:53211/otro",
            "code_challenge": challenge,
        },
        follow_redirects=False,
    )
    assert autorizacion.status_code == 400


def test_revoke_invalida_el_token(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, tokens = client
    access, refresh, _ = tokens.issue_pair("user-1", "eth_client_x")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    respuesta = test_client.post("/oauth/revoke", content=f"token={access}", headers=headers)
    assert respuesta.status_code == 200
    assert tokens.resolve_access(access) is None
    # El refresh sigue vivo hasta revocarlo o consumirlo.
    assert tokens.consume_refresh(refresh) is not None

    # Token desconocido: también 200 (RFC 7009 §2.2, sin fuga de existencia).
    otro = test_client.post("/oauth/revoke", content="token=eth_oauth_x", headers=headers)
    assert otro.status_code == 200


def test_mcp_sin_barra_final_responde(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    """Los usuarios pegan el endpoint con y sin barra final; ambos deben servir."""
    test_client, tokens = client
    access, _, _ = tokens.issue_pair("user-1", "eth_client_x")
    respuesta = test_client.get("/mcp", headers={"Authorization": f"Bearer {access}"})
    assert respuesta.status_code not in (401, 404)


def test_mcp_sin_token_recibe_desafio_401(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, _ = client
    respuesta = test_client.get("/mcp/")
    assert respuesta.status_code == 401
    assert "resource_metadata" in respuesta.headers["www-authenticate"]


def test_mcp_con_access_token_oauth_pasa_el_desafio(
    client: tuple[TestClient, InMemoryOAuthTokenStore],
) -> None:
    test_client, tokens = client
    access, _, _ = tokens.issue_pair("user-1", "eth_client_x")
    # Con Bearer válido el middleware deja pasar (la respuesta ya es del
    # transporte MCP, no 401).
    respuesta = test_client.get("/mcp/", headers={"Authorization": f"Bearer {access}"})
    assert respuesta.status_code != 401
    # Y el resolver compartido lo mapea al usuario (lo usan las tools).
    assert resolve_bearer_user(f"Bearer {access}") == "user-1"
