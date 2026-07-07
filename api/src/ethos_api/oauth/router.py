"""Endpoints OAuth 2.1 del MCP (D56).

Authorization server mínimo integrado en el API, según el patrón del spec MCP:
discovery (RFC 8414 + RFC 9728), registro dinámico de clientes públicos
(RFC 7591), authorization code con PKCE S256 obligatorio y refresh rotatorio.
El consentimiento vive en la web (`/oauth/autorizar`), autenticado con la
sesión de Supabase; el token legacy `eth_live_…` sigue vigente (D22).
"""

from __future__ import annotations

import base64
import hashlib
from urllib.parse import parse_qs, urlencode, urlparse

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from ethos_api.auth import CurrentUserId
from ethos_api.config import settings
from ethos_api.oauth.deps import ClientStoreDep, CodeStoreDep, TokenStoreDep
from ethos_api.oauth.models import (
    ApprovalInput,
    ApprovalOut,
    ClientRegistrationInput,
    OAuthClient,
)

router = APIRouter(tags=["oauth"])

_DEFAULT_SCOPE = "ethos:read"


def _issuer(request: Request) -> str:
    """URL pública del API: configurada, o derivada de la petición en local."""
    if settings.public_base_url:
        return settings.public_base_url.rstrip("/")
    return str(request.base_url).rstrip("/")


def _web_base() -> str:
    """URL de la web (página de consentimiento): configurada o primer origen CORS."""
    if settings.web_base_url:
        return settings.web_base_url.rstrip("/")
    first_origin = settings.allowed_origins.split(",")[0].strip()
    return first_origin.rstrip("/")


def _valid_redirect(uri: str) -> bool:
    """OAuth 2.1: https, o http solo para loopback (localhost/127.0.0.1)."""
    parsed = urlparse(uri)
    if parsed.scheme == "https":
        return bool(parsed.netloc)
    if parsed.scheme == "http":
        return parsed.hostname in ("localhost", "127.0.0.1")
    return False


def _redirect_with(uri: str, params: dict[str, str]) -> str:
    separator = "&" if urlparse(uri).query else "?"
    return uri + separator + urlencode(params)


# ===== Discovery (RFC 8414 + RFC 9728) =====


@router.get("/.well-known/oauth-authorization-server")
def authorization_server_metadata(request: Request) -> dict[str, object]:
    """Metadata del authorization server (RFC 8414)."""
    issuer = _issuer(request)
    return {
        "issuer": issuer,
        "authorization_endpoint": f"{issuer}/oauth/authorize",
        "token_endpoint": f"{issuer}/oauth/token",
        "registration_endpoint": f"{issuer}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": [_DEFAULT_SCOPE],
    }


@router.get("/.well-known/oauth-protected-resource")
@router.get("/.well-known/oauth-protected-resource/mcp")
def protected_resource_metadata(request: Request) -> dict[str, object]:
    """Metadata del recurso protegido (RFC 9728): el MCP y su AS."""
    issuer = _issuer(request)
    return {
        "resource": f"{issuer}/mcp/",
        "authorization_servers": [issuer],
        "scopes_supported": [_DEFAULT_SCOPE],
        "bearer_methods_supported": ["header"],
    }


# ===== Registro dinámico (RFC 7591) =====


@router.post("/oauth/register", status_code=status.HTTP_201_CREATED)
def register_client(
    body: ClientRegistrationInput, clients: ClientStoreDep
) -> dict[str, object]:
    """Registra un cliente público (sin secreto); PKCE es obligatorio."""
    invalid = [uri for uri in body.redirect_uris if not _valid_redirect(uri)]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"redirect_uris inválidas (https o http://localhost): {invalid}",
        )
    client = clients.register(body.client_name, body.redirect_uris)
    return {
        "client_id": client.client_id,
        "client_name": client.client_name,
        "redirect_uris": client.redirect_uris,
        "token_endpoint_auth_method": "none",
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
    }


# ===== Authorization endpoint =====


@router.get("/oauth/authorize")
def authorize(request: Request, clients: ClientStoreDep) -> RedirectResponse:
    """Valida la petición y manda el navegador al consentimiento de la web.

    Cliente o redirect_uri desconocidos → 400 (nunca se redirige a una URI no
    registrada); el resto de errores viajan a la redirect_uri del cliente.
    """
    params = dict(request.query_params)
    client = clients.get(params.get("client_id", ""))
    redirect_uri = params.get("redirect_uri", "")
    if client is None or redirect_uri not in client.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id desconocido o redirect_uri no registrada",
        )

    error = _authorize_error(params)
    if error:
        failure = {"error": error}
        if params.get("state"):
            failure["state"] = params["state"]
        return RedirectResponse(_redirect_with(redirect_uri, failure))

    consent = {
        "client_id": client.client_id,
        "client_name": client.client_name,
        "redirect_uri": redirect_uri,
        "code_challenge": params["code_challenge"],
        "code_challenge_method": "S256",
        "scope": params.get("scope", _DEFAULT_SCOPE),
    }
    if params.get("state"):
        consent["state"] = params["state"]
    return RedirectResponse(_web_base() + "/oauth/autorizar?" + urlencode(consent))


def _authorize_error(params: dict[str, str]) -> str | None:
    if params.get("response_type") != "code":
        return "unsupported_response_type"
    if not params.get("code_challenge"):
        # PKCE obligatorio en OAuth 2.1.
        return "invalid_request"
    if params.get("code_challenge_method", "S256") != "S256":
        return "invalid_request"
    return None


# ===== Consentimiento (lo llama la web con la sesión de Supabase) =====


@router.post("/oauth/approve", response_model=ApprovalOut)
def approve(
    body: ApprovalInput,
    user_id: CurrentUserId,
    clients: ClientStoreDep,
    codes: CodeStoreDep,
) -> ApprovalOut:
    """Registra la decisión del usuario y devuelve a dónde navegar."""
    client = clients.get(body.client_id)
    if client is None or body.redirect_uri not in client.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id desconocido o redirect_uri no registrada",
        )

    if not body.approve:
        failure = {"error": "access_denied"}
        if body.state:
            failure["state"] = body.state
        return ApprovalOut(redirect_to=_redirect_with(body.redirect_uri, failure))

    code = codes.mint(
        user_id, client.client_id, body.redirect_uri, body.code_challenge, body.scope
    )
    success = {"code": code}
    if body.state:
        success["state"] = body.state
    return ApprovalOut(redirect_to=_redirect_with(body.redirect_uri, success))


# ===== Token endpoint =====


def _pkce_ok(verifier: str, challenge: str) -> bool:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return expected == challenge


def _token_error(error: str, description: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": error, "error_description": description},
        headers={"Cache-Control": "no-store"},
    )


@router.post("/oauth/token")
async def token(
    request: Request,
    clients: ClientStoreDep,
    codes: CodeStoreDep,
    tokens: TokenStoreDep,
) -> JSONResponse:
    """Canjea un authorization code (con PKCE) o un refresh token."""
    # El cuerpo llega application/x-www-form-urlencoded (RFC 6749); se parsea
    # a mano para no depender de python-multipart.
    raw = (await request.body()).decode("utf-8", errors="replace")
    form = {k: v[0] for k, v in parse_qs(raw).items()}
    grant_type = form.get("grant_type", "")

    if grant_type == "authorization_code":
        return _exchange_code(form, clients, codes, tokens)
    if grant_type == "refresh_token":
        return _exchange_refresh(form, tokens)
    return _token_error("unsupported_grant_type", f"grant_type: {grant_type or '—'}")


def _exchange_code(
    form: dict[str, str],
    clients: ClientStoreDep,
    codes: CodeStoreDep,
    tokens: TokenStoreDep,
) -> JSONResponse:
    client = clients.get(form.get("client_id", ""))
    if client is None:
        return _token_error("invalid_client", "client_id desconocido")
    grant = codes.consume(form.get("code", ""))
    if grant is None:
        return _token_error("invalid_grant", "code inválido, usado o expirado")
    if grant.client_id != client.client_id or grant.redirect_uri != form.get(
        "redirect_uri", ""
    ):
        return _token_error("invalid_grant", "el code no corresponde a este cliente")
    if not _pkce_ok(form.get("code_verifier", ""), grant.code_challenge):
        return _token_error("invalid_grant", "code_verifier no supera el PKCE")

    access, refresh, expires_in = tokens.issue_pair(grant.user_id, client.client_id)
    return _token_response(access, refresh, expires_in, grant.scope)


def _exchange_refresh(form: dict[str, str], tokens: TokenStoreDep) -> JSONResponse:
    consumed = tokens.consume_refresh(form.get("refresh_token", ""))
    if consumed is None:
        return _token_error("invalid_grant", "refresh token inválido o expirado")
    user_id, client_id = consumed
    access, refresh, expires_in = tokens.issue_pair(user_id, client_id)
    return _token_response(access, refresh, expires_in, _DEFAULT_SCOPE)


def _token_response(
    access: str, refresh: str, expires_in: int, scope: str
) -> JSONResponse:
    return JSONResponse(
        content={
            "access_token": access,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "refresh_token": refresh,
            "scope": scope,
        },
        headers={"Cache-Control": "no-store"},
    )


__all__ = ["OAuthClient", "router"]
