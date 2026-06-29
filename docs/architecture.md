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

### 4.1 Registro de conectores y catálogo de categorías

Un registro (registry) asocia cada (categoría, proveedor) con su conector, su
modo de ingesta y sus `capabilities`. Las capas río abajo (normalización,
persistencia, MCP, web) resuelven por el registro; añadir una categoría o un
proveedor es implementar y registrar un conector. (D21)

Catálogo objetivo de categorías y su proveedor inicial:

| Categoría | Proveedor | Modo |
|-----------|-----------|------|
| Juegos | Steam | API |
| Música | ListenBrainz | API |
| Cine y TV | Trakt | API |
| Anime y manga | AniList | API |
| Actividad física | Strava | API |
| Libros | Goodreads | Import |
| Lugares | Swarm | API |
| Comida | Beli | Import |
| Juegos de mesa | BoardGameGeek | Import |

Generalización del contrato: la mayoría son "obra + relación" (rating, estado,
engagement); Lugares y Comida encajan tratando el sitio o el plato como obra.
Actividad física (Strava) es de tipo evento/métrica (distancia, duración) y no
es una "obra", por lo que el contrato normalizado debe admitir también esa
forma. Por confirmar la forma exacta (D23).

## 5. Servidor MCP

- Transporte: streamable-HTTP, con `stateless_http=True` para escalar sin estado de sesión en memoria.
- Autenticación: token simple por usuario, validado por middleware. Migrable a OAuth 2.1 más adelante.
- Expone: un resource de resumen compacto (lo siempre relevante) y tools de consulta parametrizadas (ventana, tipo, límite) sobre datos indexados.
- Regla de seguridad: el token con que la IA se autentica ante el MCP nunca se reenvía a las APIs de terceros; las tools usan las credenciales del servidor.
- Guardrail (D22): las tools que exponen datos del usuario requieren el middleware de token por usuario. Mientras no exista, solo se publican tools no sensibles (hoy `ping`); el endpoint `/mcp` no debe servir datos sin auth.

## 6. Refresco

- Solo para fuentes API. El botón encola una tarea en Supabase Queues; un worker la procesa, actualiza los datos y marca `last_synced_at`.
- Estrategia: incremental (solo re-consultar lo que cambió desde el último sync). Pendiente de afinar la llave de cambio por proveedor.
- Para fuentes import, el equivalente a refrescar es volver a subir el export.

## 7. Seguridad y privacidad

- Tokens de terceros: cifrados a nivel de app (Fernet/AES-GCM) antes de guardarse en Postgres; la llave vive en el secret manager, nunca en el repo. Se descifran solo en memoria al llamar la API. Mejora futura opcional: envelope encryption con KMS.
- Aislamiento entre usuarios: Row-Level Security en Postgres.
- Login de la app: Supabase Auth.

### 7.1 Sesión y credenciales de terceros (planificado)

- Sesión: Supabase Auth autentica al usuario de la app (JWT/cookie de sesión).
- "Guardar las APIs": las credenciales de terceros que aporta el usuario (tokens
  o keys, p. ej. ListenBrainz, Trakt) se guardan en la tabla `user_credentials`
  cifradas a nivel de app (Fernet/AES-GCM), con la llave en el secret manager
  (D9, D20). Se descifran solo en memoria al llamar la API; nunca viajan al cliente.
- RLS owner-only en `user_credentials` (aislamiento por usuario).
- Para proveedores OpenID/OAuth (Steam, Trakt, Strava), el identificador o los
  tokens OAuth resultantes se custodian en el mismo almacén cifrado.
- El token del MCP por usuario es independiente y nunca se reenvía a terceros.

## 8. Costo y compromisos

- Objetivo: 0 USD/mes.
- Compromiso de Render (free): el servicio se duerme tras inactividad y arranca en 30-50 s. Se mitiga combinando backend+MCP en un solo servicio, keep-alive ping, warm-up al cargar la web, estados "despertando" y reintento con backoff.
- Compromiso de Supabase (free): los proyectos se pausan tras 7 días de inactividad; se mitiga con el mismo ping.
- Sin lock-in: el mismo contenedor se mueve a Cloud Run sin cambiar código si se necesita rapidez (requiere tarjeta con tope de gasto).

## 9. Repositorio y herramientas

- Monorepo con carpetas claras: `/web` (TS), `/api` (Python, incluye el MCP), `/packages` o `/shared` para tipos comunes.
- Tipos del esquema compartibles generando tipos TS desde el esquema Python (vía OpenAPI).
- CI en GitHub Actions corriendo tests de todas las capas.
