"""Configuración del backend cargada desde el entorno.

Ningún secreto vive en el código: los valores provienen de variables de
entorno o de un archivo .env local (no versionado). Los secretos usan
`SecretStr` para no filtrarse en logs ni en `repr()`.
"""

from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación leídos del entorno."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Credenciales de servicios externos (vacías por defecto; se inyectan
    # por entorno en cada despliegue).
    supabase_url: str = ""
    # La anon key es publicable (viaja al navegador); no es un secreto.
    supabase_anon_key: str = ""
    supabase_service_role_key: SecretStr = SecretStr("")
    # Secreto legacy para verificar JWT de Supabase Auth (HS256). Los proyectos
    # nuevos usan llaves asimétricas verificadas vía JWKS (ver auth.py).
    supabase_jwt_secret: SecretStr = SecretStr("")
    encryption_key: SecretStr = SecretStr("")
    steam_api_key: SecretStr = SecretStr("")


settings = Settings()
