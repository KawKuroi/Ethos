# Arquitectura — Contexto

## 1. Stack

| Capa | Tecnología |
|------|-----------|
| Web (UI, dump, onboarding) | TypeScript — Next.js o Astro + Recharts |
| Backend API + servidor MCP | Python — FastAPI + FastMCP (un solo servicio) |
| Procesamiento / normalización | Polars + Pydantic v2 |
| Datos, auth, secretos, cola | Supabase (Postgres + Auth + Vault + Queues) |
| Gestor de paquetes Python | uv |
| Gestor de paquetes TS | pnpm |
| Repositorio | Monorepo |

## 2. Hospedaje

- Web: Vercel (Hobby, gratis, sin tarjeta).
- Backend + MCP: un único servicio en Render (free, 750 h/mes). Se combinan la API y el endpoint MCP (`/mcp`) en la misma app para mantener un solo servicio vivo.
- Datos: Supabase (free, sin tarjeta).
- Keep-alive: un pinger gratuito (ej. UptimeRobot) mantiene despierto el servicio de Render y evita cold starts.

## 3. Flujo de datos

1. La persona se autentica (Supabase Auth).
2. Por categoría, conecta un proveedor vía API o sube un import.
3. El backend extrae (API) o parsea (import) y normaliza al esquema común.
4. Se guarda en Postgres, normalizado e indexado, aislado por usuario (RLS).
5. Un generador produce el resumen curado a partir del almacén.
6. Dos consumidores leen el mismo almacén: el servidor MCP (para la IA) y la web (para el dump).

## 4. Modelo de conectores

- Cada categoría tiene un slot; bajo él se registran proveedores. Una sola fuente activa por categoría.
- Dos modos de ingesta: API (llamada con credenciales del servidor) o import (parseo de archivo).
- Todo proveedor mapea su dato crudo al mismo esquema normalizado, de modo que las capas posteriores no dependen del origen.
- Añadir un proveedor o una alternativa es implementar un conector y registrarlo; nada río abajo cambia.

## 5. Servidor MCP

- Transporte: streamable-HTTP, con `stateless_http=True` para escalar sin estado de sesión en memoria.
- Autenticación: token simple por usuario, validado por middleware. Migrable a OAuth 2.1 más adelante.
- Expone: un resource de resumen compacto (lo siempre relevante) y tools de consulta parametrizadas (ventana, tipo, límite) sobre datos indexados.
- Regla de seguridad: el token con que la IA se autentica ante el MCP nunca se reenvía a las APIs de terceros; las tools usan las credenciales del servidor.

## 6. Refresco

- Solo para fuentes API. El botón encola una tarea en Supabase Queues; un worker la procesa, actualiza los datos y marca `last_synced_at`.
- Estrategia: incremental (solo re-consultar lo que cambió desde el último sync). Pendiente de afinar la llave de cambio por proveedor.
- Para fuentes import, el equivalente a refrescar es volver a subir el export.

## 7. Seguridad y privacidad

- Tokens de terceros: cifrados a nivel de app (Fernet/AES-GCM) antes de guardarse en Postgres; la llave vive en el secret manager, nunca en el repo. Se descifran solo en memoria al llamar la API. Mejora futura opcional: envelope encryption con KMS.
- Aislamiento entre usuarios: Row-Level Security en Postgres.
- Login de la app: Supabase Auth.

## 8. Costo y compromisos

- Objetivo: 0 USD/mes.
- Compromiso de Render (free): el servicio se duerme tras inactividad y arranca en 30-50 s. Se mitiga combinando backend+MCP en un solo servicio, keep-alive ping, warm-up al cargar la web, estados "despertando" y reintento con backoff.
- Compromiso de Supabase (free): los proyectos se pausan tras 7 días de inactividad; se mitiga con el mismo ping.
- Sin lock-in: el mismo contenedor se mueve a Cloud Run sin cambiar código si se necesita rapidez (requiere tarjeta con tope de gasto).

## 9. Repositorio y herramientas

- Monorepo con carpetas claras: `/web` (TS), `/api` (Python, incluye el MCP), `/packages` o `/shared` para tipos comunes.
- Tipos del esquema compartibles generando tipos TS desde el esquema Python (vía OpenAPI).
- CI en GitHub Actions corriendo tests de todas las capas.
