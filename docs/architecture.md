# Arquitectura — Contexto

## 1. Stack

| Capa | Tecnología |
|------|-----------|
| Web (landing, auth, panel) | TypeScript — Next.js (App Router); tokens como CSS variables + CSS Modules; gráficos SVG propios (sparklines y barras); `next/font` (Bricolage Grotesque + Hanken Grotesk); `next-themes` (claro/oscuro/sistema) |
| Backend API + servidor MCP | Python — FastAPI + FastMCP (un solo servicio) |
| Procesamiento / normalización | Polars + Pydantic v2 |
| Datos, auth, secretos, cola | Supabase (Postgres + Auth + Vault + Queues) |
| Gestor de paquetes Python | uv |
| Gestor de paquetes TS | pnpm |
| Repositorio | Monorepo |

La UI no usa librería de componentes ni de gráficos: el diseño (ver
`design.md`) está expresado en CSS variables y SVG simples, y se traduce
directo (D29). Recharts queda descartado salvo que aparezcan gráficos que lo
justifiquen.

## 2. Hospedaje

- Web: Vercel (Hobby, gratis, sin tarjeta).
- Backend + MCP: un único servicio en Render (free, 750 h/mes). Se combinan la API y el endpoint MCP (`/mcp`) en la misma app para mantener un solo servicio vivo.
- Datos: Supabase (free, sin tarjeta).
- Keep-alive: un pinger gratuito (ej. UptimeRobot) mantiene despierto el servicio de Render y evita cold starts.

## 3. Flujo de datos

1. La persona se autentica (Supabase Auth: correo/contraseña o Google — D26 revisada).
2. Por categoría, conecta un proveedor vía API o sube un import (guiado por proveedor).
3. El backend extrae (API) o parsea (import) y normaliza al esquema común.
4. Se guarda en Postgres, normalizado e indexado, aislado por usuario (RLS).
5. Un generador produce el resumen curado a partir del almacén.
6. Tres consumidores leen el mismo almacén (D24): la web (el panel), el servidor MCP (consulta en vivo de la IA) y la descarga de contexto (archivos por categoría).

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

Catálogo (D27) — proveedor inicial y alternativas visibles en la UI:

| Categoría | Proveedor inicial | Modo | Alternativas |
|-----------|------------------|------|--------------|
| Juegos | Steam | API | Xbox (API no oficial), PlayStation (API no oficial), GOG (import) |
| Música | ListenBrainz | API | Last.fm (API), Spotify (import), Apple Music (import) |
| Cine y TV | Trakt | API | TMDB (API), Letterboxd (import), IMDb (import) |
| Anime y manga | AniList | API | MyAnimeList (API), Kitsu (API) |
| Libros | Goodreads | Import | Hardcover (API), StoryGraph (import), Open Library (API) |

Modos según la investigación de fuentes del 2026-07-03 (bitácora en
`current.md`): descartados de plano Epic y Backloggd (sin API ni export),
Deezer y Tidal (API cerrada / sin historial) y TV Time (cierra 2026-07-15).
Xbox y PlayStation dependen de APIs no oficiales (OpenXBL, psn-api):
funcionales pero revocables.

Diferidas (fuera del catálogo por D27, se reevaluarán): Lugares (Swarm),
Comida (Beli, solo import) y Juegos de mesa (BoardGameGeek, solo import).
Retirada (D31): Actividad física — sin fuente viable (Strava prohíbe usar
datos de su API con IA; Garmin no admite desarrolladores personales; la Web
API de Fitbit se apaga en septiembre de 2026).

Estados por categoría: activa, apagada (sin datos) o en desarrollo (conector
no listo; visible pero no activable). El catálogo se habilita secuencialmente
(D27): en la v1 solo Juegos está implementada y las otras cuatro aparecen "en
desarrollo"; cada nueva categoría se construye, prueba y confirma antes de
pasar a la siguiente. Generalización del contrato: todas encajan en
"obra + relación" (rating, estado, engagement); Lugares y Comida encajarían
tratando el sitio o el plato como obra. La forma evento/métrica que exigía
Actividad física dejó de ser necesaria al retirarse la categoría (D23/D31).

## 5. Salidas del contexto (D24)

- **Descarga**: `GET /context/{category}` (autenticado) devuelve el archivo
  `<categoria>.context.json` — resumen, tops, etiquetas y el histórico
  normalizado de esa categoría. La web muestra vista previa (pestañas
  JSON / MCP) antes de descargar.
- **Servidor MCP**: la IA consulta en vivo, sin archivos. Ambas salidas se
  generan del mismo almacén; el archivo es un corte estático, el MCP responde
  acotado por consulta.

## 6. Servidor MCP

- Transporte: streamable-HTTP, con `stateless_http=True` para escalar sin estado de sesión en memoria.
- Autenticación: token simple por usuario (`eth_live_…`), validado por middleware; endpoint por usuario (`/mcp/u/<id>`). Migrable a OAuth 2.1 más adelante.
- Expone: un resource de resumen compacto (lo siempre relevante) y tools de consulta parametrizadas (ventana, tipo, límite) sobre datos indexados.
- Tools con namespace por categoría (D28): `games.top_by_hours`, `music.recent`, `books.currently_reading`, `<categoria>.summary`, …, más `profile.search` global. Mantener el total bajo (~25-30 máximo).
- Cada respuesta informa cuánto contexto viajó (KB servidos vs. tamaño total del contexto de la categoría); la web lo enseña en el playground de Conectar IA.
- Regla de seguridad: el token con que la IA se autentica ante el MCP nunca se reenvía a las APIs de terceros; las tools usan las credenciales del servidor.
- Guardrail (D22): las tools que exponen datos del usuario requieren el middleware de token por usuario. Mientras no exista, solo se publican tools no sensibles (hoy `ping`); el endpoint `/mcp` no debe servir datos sin auth.

## 7. Refresco

- Solo para fuentes API. El botón (por categoría, o global desde Inicio) encola una tarea en Supabase Queues; un worker la procesa, actualiza los datos y marca `last_synced_at`.
- Estrategia: incremental (solo re-consultar lo que cambió desde el último sync). Pendiente de afinar la llave de cambio por proveedor.
- Para fuentes import, el equivalente a refrescar es volver a subir el export.

## 8. Seguridad y privacidad

- Tokens de terceros: cifrados a nivel de app (Fernet: AES-128-CBC + HMAC) antes de guardarse en Postgres; la llave vive en el secret manager, nunca en el repo. Se descifran solo en memoria al llamar la API. Mejora futura opcional: envelope encryption con KMS.
- Anti-abuso (D30): rate limit por IP (429 + Retry-After), límite de tamaño de cuerpo (413), cabeceras de seguridad, CORS restringido al origen de la web, hosts confiables, docs interactivos apagados en producción y throttle del cliente de Steam (cuota de la API key).
- Aislamiento entre usuarios: Row-Level Security en Postgres.
- Login de la app: Supabase Auth con correo/contraseña y Google (D26 revisada; GitHub retirado). Steam no es login de la app: su OpenID es el flujo de conexión de la fuente de Juegos (D12).
- Borrado: "eliminar todos los datos" borra el contexto conservando la cuenta; "eliminar cuenta" es borrado diferido con correo de deshacer de 30 días.

### 8.1 Sesión y credenciales de terceros

- Sesión: Supabase Auth autentica al usuario de la app (JWT/cookie de sesión).
- Verificación del JWT en el backend: soporta las llaves de firma asimétricas
  de Supabase (ES256/RS256 vía JWKS, con caché de llaves) y el secreto HS256
  legacy como fallback; exige `exp` y `sub`, y valida `aud` e `iss`.
- "Guardar las APIs": las credenciales de terceros que aporta el usuario (tokens
  o keys, p. ej. ListenBrainz, Trakt) se guardan en la tabla `user_credentials`
  cifradas a nivel de app (Fernet), con la llave en el secret manager
  (D9, D20). Se descifran solo en memoria al llamar la API; nunca viajan al cliente.
- RLS owner-only en `user_credentials` (aislamiento por usuario).
- Para proveedores OpenID/OAuth (Steam, Trakt), el identificador o los
  tokens OAuth resultantes se custodian en el mismo almacén cifrado.
- El token del MCP por usuario es independiente y nunca se reenvía a terceros.

## 9. Costo y compromisos

- Objetivo: 0 USD/mes.
- Compromiso de Render (free): el servicio se duerme tras inactividad y arranca en 30-50 s. Se mitiga combinando backend+MCP en un solo servicio, keep-alive ping, warm-up al cargar la web, estados "despertando" y reintento con backoff.
- Compromiso de Supabase (free): los proyectos se pausan tras 7 días de inactividad; se mitiga con el mismo ping.
- Sin lock-in: el mismo contenedor se mueve a Cloud Run sin cambiar código si se necesita rapidez (requiere tarjeta con tope de gasto).

## 10. Repositorio y herramientas

- Monorepo con carpetas claras: `/web` (TS), `/api` (Python, incluye el MCP), `/packages` o `/shared` para tipos comunes.
- `/web` implementa el diseño de Claude Design (ver `design.md`): landing pública en `/`, auth, y el panel autenticado.
- Tipos del esquema compartibles generando tipos TS desde el esquema Python (vía OpenAPI).
- CI en GitHub Actions corriendo tests de todas las capas.
