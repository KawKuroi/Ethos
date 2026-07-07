"""Borrado del usuario en Supabase Auth (GoTrue admin API).

Usa la service_role key para llamar al endpoint admin de GoTrue. Borrar el
usuario cascada al resto de tablas propias (FK `on delete cascade`). Solo lo
invoca el job de purga (D53), nunca una petición del propio usuario.
"""

from __future__ import annotations

import httpx

from ethos_api.config import settings


class AuthAdminError(RuntimeError):
    """Error al borrar el usuario en GoTrue."""


def delete_auth_user(user_id: str) -> None:
    """Borra el usuario de Supabase Auth por su id (admin API)."""
    url = settings.supabase_url
    key = settings.supabase_service_role_key.get_secret_value()
    if not url or not key:
        raise AuthAdminError("Sin SUPABASE_URL o service_role key para borrar el usuario")
    response = httpx.delete(
        f"{url.rstrip('/')}/auth/v1/admin/users/{user_id}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=15.0,
    )
    if response.status_code >= 400:
        raise AuthAdminError(
            f"GoTrue respondió {response.status_code}: {response.text[:200]}"
        )
