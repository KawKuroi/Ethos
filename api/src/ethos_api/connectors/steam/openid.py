"""Verificación del retorno OpenID 2.0 de Steam (D12).

Steam no da OAuth: la conexión de la fuente usa su OpenID. El navegador va a
`steamcommunity.com/openid/login` y vuelve a la web con los parámetros
firmados; la web se los reenvía a esta API, que los verifica directamente
contra Steam (`check_authentication`) antes de aceptar el steamid. Nunca se
confía en el steamid sin esa verificación de firma.
"""

from __future__ import annotations

import re

import httpx

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
_CLAIMED_ID_RE = re.compile(r"^https://steamcommunity\.com/openid/id/(\d{17})$")
# Campos que deben venir cubiertos por la firma para que el retorno sea de fiar.
_REQUIRED_SIGNED = {"op_endpoint", "claimed_id", "identity", "return_to", "response_nonce"}


class SteamOpenIdError(ValueError):
    """El retorno OpenID no es válido o no pasó la verificación."""


def build_login_url(return_to: str, realm: str) -> str:
    """URL de login de Steam a la que la web manda al navegador."""
    params = httpx.QueryParams(
        {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.return_to": return_to,
            "openid.realm": realm,
        }
    )
    return f"{STEAM_OPENID_URL}?{params}"


def verify_openid_response(
    params: dict[str, str], *, client: httpx.Client | None = None
) -> str:
    """Verifica el retorno OpenID contra Steam y devuelve el steamid.

    Lanza `SteamOpenIdError` si faltan campos, la firma no cubre los campos
    obligatorios, Steam no confirma la autenticación o el claimed_id no es un
    perfil de Steam.
    """
    if params.get("openid.mode") != "id_res":
        raise SteamOpenIdError("El retorno OpenID no viene en modo id_res")

    op_endpoint = params.get("openid.op_endpoint")
    if op_endpoint != STEAM_OPENID_URL:
        raise SteamOpenIdError("El op_endpoint no es el de Steam")

    signed = set((params.get("openid.signed") or "").split(","))
    if not _REQUIRED_SIGNED.issubset(signed):
        raise SteamOpenIdError("La firma OpenID no cubre los campos obligatorios")

    claimed_id = params.get("openid.claimed_id", "")
    match = _CLAIMED_ID_RE.match(claimed_id)
    if not match:
        raise SteamOpenIdError("El claimed_id no es un perfil de Steam")

    # check_authentication: se reenvían los parámetros firmados a Steam y solo
    # se acepta el steamid si responde is_valid:true.
    verification = {**params, "openid.mode": "check_authentication"}
    http = client or httpx.Client(timeout=15.0)
    response = http.post(STEAM_OPENID_URL, data=verification)
    if response.status_code != 200 or "is_valid:true" not in response.text:
        raise SteamOpenIdError("Steam no confirmó la autenticación OpenID")

    return match.group(1)
