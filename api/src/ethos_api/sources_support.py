"""Alta de credenciales de fuente compartida por los slices (D4/D62).

Una sola fuente activa por categoría: al conectar un proveedor se elimina la
credencial de cualquier otro proveedor de la misma categoría (el primer
refresco del nuevo reemplaza los datos). El secreto (username o token) viaja
cifrado a `user_credentials` (D20).
"""

from __future__ import annotations

from datetime import UTC, datetime

from ethos_api.connectors.registry import registry
from ethos_api.credentials.models import UserCredential
from ethos_api.credentials.repository import CredentialRepository
from ethos_api.schema import Category
from ethos_api.security import TokenCipher


def replace_category_credential(
    repo: CredentialRepository,
    cipher: TokenCipher,
    user_id: str,
    provider: str,
    category: Category,
    secret: str,
) -> None:
    """Guarda la credencial del proveedor y desconecta a sus hermanos (D4)."""
    for sibling in registry.providers(category):
        if sibling != provider:
            repo.delete(user_id, sibling)
    now = datetime.now(UTC)
    existing = repo.get(user_id, provider)
    repo.upsert(
        UserCredential(
            user_id=user_id,
            provider=provider,
            category=category,
            encrypted_token=cipher.encrypt(secret),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
    )
