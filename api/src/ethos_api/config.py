"""Configuración del backend cargada desde el entorno.

Ningún secreto vive en el código: los valores provienen de variables de
entorno o de un archivo .env local (no versionado).
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación leídos del entorno."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Credenciales de servicios externos (vacías por defecto; se inyectan
    # por entorno en cada despliegue).
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    encryption_key: str = ""
    steam_api_key: str = ""


settings = Settings()
