"""Modelos de las credenciales de terceros por usuario."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ethos_api.schema import Category


class ConnectCredentialInput(BaseModel):
    """Entrada para conectar una credencial (el token llega en claro y se cifra)."""

    provider: str
    category: Category
    token: str


class UserCredential(BaseModel):
    """Credencial almacenada: el token va cifrado, nunca en claro."""

    user_id: str
    provider: str
    category: Category
    encrypted_token: str
    created_at: datetime
    updated_at: datetime


class CredentialSummary(BaseModel):
    """Vista pública de una credencial: sin el token."""

    provider: str
    category: Category
    created_at: datetime
    updated_at: datetime
