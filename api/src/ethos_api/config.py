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

    # Protección de la API (ver middleware.py y main.py).
    # Orígenes permitidos para CORS, separados por coma.
    allowed_origins: str = "http://localhost:3000"
    # Hosts confiables (header Host), separados por coma; "*" solo en desarrollo.
    allowed_hosts: str = "*"
    # Límite de peticiones por IP por minuto (0 desactiva el límite).
    rate_limit_per_minute: int = 120
    # Tamaño máximo del cuerpo de una petición, en bytes.
    max_body_bytes: int = 64_000
    # Tamaño máximo para las rutas de import de archivos (`/imports` y
    # `/sources/*/import`); un export de Goodreads puede superar los 64 KB.
    max_import_bytes: int = 5_000_000

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
    # client_id de la app de Trakt (categoría Cine y TV); lee datos públicos
    # de un usuario sin OAuth (header trakt-api-key), D41.
    trakt_client_id: SecretStr = SecretStr("")

    # OAuth 2.1 del MCP (D56). URL pública del API (issuer del authorization
    # server) y de la web (página de consentimiento). Vacías en local: el
    # issuer se deriva de la petición y la web del primer origen de CORS.
    public_base_url: str = ""
    web_base_url: str = ""

    # Notificación por correo de sugerencias/contacto (D52). Todo vacío por
    # defecto: sin SMTP configurado, el feedback se persiste pero no se avisa.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: SecretStr = SecretStr("")
    # Remitente y destinatario de los avisos (el admin recibe en feedback_to).
    feedback_from: str = ""
    feedback_to: str = ""


settings = Settings()
