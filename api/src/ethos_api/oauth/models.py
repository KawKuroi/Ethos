"""Modelos del flujo OAuth 2.1 del MCP (D56)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OAuthClient(BaseModel):
    """Cliente público registrado dinámicamente (RFC 7591); sin secreto."""

    client_id: str
    client_name: str
    redirect_uris: list[str]


class ClientRegistrationInput(BaseModel):
    """Entrada del registro dinámico; los campos extra del RFC se ignoran."""

    model_config = {"extra": "ignore"}

    client_name: str = Field(default="Cliente MCP", max_length=120)
    redirect_uris: list[str] = Field(min_length=1)


class AuthorizationCode(BaseModel):
    """Concesión pendiente de canje, ligada al PKCE del cliente."""

    user_id: str
    client_id: str
    redirect_uri: str
    code_challenge: str
    scope: str
    expires_at: datetime


class ApprovalInput(BaseModel):
    """Decisión del usuario en la página de consentimiento."""

    client_id: str
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str = "S256"
    state: str | None = None
    scope: str = "ethos:read"
    approve: bool


class ApprovalOut(BaseModel):
    """A dónde debe navegar el navegador tras decidir."""

    redirect_to: str
