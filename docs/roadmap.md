# Roadmap — Contexto

Fases de construcción. Cada tarea se marca `[x]` al completarse; al cerrarse una
fase entera se mueve a `## Histórico de fases completadas`.

## Fase 1 — Slice vertical: Juegos / Steam (la v1)

Backend:

- [x] Conexión de Steam por OpenID (fuente de Juegos, no login de la app) y manejo de perfil privado. (verificación `check_authentication` + estado `private`)
- [x] Conector de Steam: biblioteca, deseados, horas, completado agregado, perfil. (wishlist sin títulos, D32; completado top-20, D33)
- [x] Normalización al esquema común y persistencia indexada. (tras puerto `GamesStore`, en memoria; respaldo Supabase pendiente, D35)
- [x] Generador del resumen de juegos.
- [x] Servidor MCP: resource de resumen + tools `games.*` y `profile.search`, reportando KB servidos. (D28)
- [x] Descarga de contexto: `GET /context/games` → `games.context.json`. (D24/D34)
- [x] Refresco asíncrono con estados de frescura. (BackgroundTasks, D36; la cola durable llega con la infra de D35)
- [x] Respaldo Supabase de los repositorios en memoria: migración 0003 (`user_items`, `mcp_tokens`, `source_state` ampliada) + repos PostgREST con selección automática por entorno. (D20/D35 — código listo; falta que el usuario aplique la migración, ver `por-revisar.md`)
- [x] Auth del MCP por token de usuario (`eth_live_…`, hash SHA-256) antes de exponer tools de datos. (D22)
- [x] Registro de conectores (registry) y modelo de extensión de categorías/proveedores. (D21)
- [x] Hardening de la API: rate limit por IP, límites de cuerpo, cabeceras, CORS, TrustedHost, docs off en producción y throttle de Steam. (D30)
- [x] Generalización del enum: `MediaCategory` → `Category` con las 9 categorías (la web enseña el catálogo completo desde el día 1). (D23/D27)

Web — implementación del diseño (`design.md`, D25/D29):

- [x] Fundación de `/web`: Next.js + tokens CSS (paleta slate, acentos por categoría), `next/font`, `next-themes`, transiciones y `prefers-reduced-motion`.
- [x] Auth: login/registro (correo + Google + GitHub), recuperación de contraseña. (D26)
- [x] Shell de la app: navegación lateral, header, badge de "Conectar IA".
- [x] Inicio: banner de IA, alertas agregadas, "El gusto en números", panorama de categorías, actividad reciente (Juegos activa; las otras cuatro como "en desarrollo").
- [x] Detalle de categoría (Juegos): status strip, stat band, Destacados/Reciente/Listas, refrescar, modal de descarga con preview JSON/MCP.
- [x] Fuentes: grupos activas / apagadas / en desarrollo, salud y método.
- [x] Conectar IA: tres pasos y playground simulado (sin LLM en v1). Nota: endpoint + token reales quedan pendientes del backend del MCP (hoy placeholder).
- [x] Ayuda (FAQ + sugerencias) y Ajustes (perfil, zona horaria, tema, zona de peligro).
- [x] Landing pública según el diseño (hero con flujo animado, qué es un MCP, cómo se usa, walkthrough de categorías + galería, FAQ, sugerencias).
- [x] Cableado web ↔ API: Inicio, Fuentes, Detalle de Juegos y Conectar IA leen datos reales con la sesión de Supabase; conexión de Steam por OpenID desde la web.
- [x] Tests de todas las capas pasando en CI. (api: 86, cobertura 95%; web: 38)

Diferidas fuera del catálogo (D27, revisión 2026-07-03): Lugares (Swarm),
Comida (Beli) y Juegos de mesa (BoardGameGeek). Se reevaluarán al cerrar las 5.
Retirada (D31, 2026-07-03): Actividad física — sin fuente viable.

## Fase 4 — Pulido y robustez

- [ ] "Avísame cuando esté lista" para categorías en desarrollo.
- [ ] Entradas a mano (añadir registros sin proveedor).
- [ ] Envío real de sugerencias y contacto (persistencia + notificación).
- [ ] Borrado de cuenta con deshacer de 30 días (correo + purga diferida).
- [ ] Playground de Conectar IA con LLM real (opcional; la v1 lo simula).
- [ ] Migración del auth del MCP a OAuth 2.1 (si se requiere).
- [ ] Enriquecimiento de géneros de juegos.
- [ ] Envelope encryption con KMS (si se requiere).
- [ ] Opción de mover el backend a Cloud Run para eliminar cold starts.
- [ ] Empaquetado y distribución pulidos; objetivos de cobertura de tests.

## Pendientes y decisiones por resolver

- Géneros de juegos: fuente de enriquecimiento (store API de Steam vs IGDB/RAWG). (D16)
- Refresco incremental: llave de cambio por proveedor. (D17)
- Qué histórico incluye el contexto descargable cuando lleguen los eventos con timestamp (la forma v1 quedó fijada en D34; se revisa en Fase 2).
- Esquema fino del perfil por categoría: qué va en el resumen (resource) vs en las tools, para música, cine y libros.
- Granularidad de música (artista / álbum / track) — por defecto los tres; confirmar el corte del resumen.
- Resolución de títulos de la wishlist de Steam (D32): candidata a la caché de catálogos globales.
- Política de retención del histórico inactivo (cuánto tiempo se conserva).
- Destino de las sugerencias (tabla + ¿aviso por correo?) y del contacto personal.
- Objetivos concretos de cobertura de tests y umbrales de CI.
- Estrategia de caché de catálogos globales (esquema de logros, metadatos de juegos) compartidos entre usuarios.
- El ping de keep-alive golpea `/health`, que no toca Supabase: añadir un toque de BD (o cron) para evitar su pausa a los 7 días.

## Histórico de fases completadas

### Fase 3 — Categorías restantes (cerrada 2026-07-05)

Las cinco categorías del catálogo (D27) quedan activas; ninguna sigue "en
desarrollo". Secuencial sobre los puertos existentes, sin migraciones:

- [x] Cine y TV: Trakt (API) — backend D41-D44 + cableado web (`FilmDetail`,
  alta por username, activa en Inicio/Fuentes/playground).
- [x] Anime y manga: AniList (API, GraphQL público sin key, D45-D46) —
  conector con dedupe de listas personalizadas, slice `anime/`, tools
  `anime.*` y web completa.
- [x] Libros: Goodreads (import CSV, D47-D48) — conector de parseo, slice
  `books/`, tools `books.*` y web con panel de import + guía.
- [x] Modo import genérico con autodetección de archivo (D49): `POST /imports`
  detecta el proveedor por firma de cabeceras y delega; límite de cuerpo
  propio para rutas de import; guías por proveedor en la web.

Además: `profile.search` generalizado a las categorías de obra, y
generalización web (tarjetas/filas por descriptor, modal de contexto y form
de username compartidos). api 168 tests (93.2%), web 55 tests, build verde.

### Fase 2 — Música / ListenBrainz (cerrada 2026-07-04)

Segunda categoría de punta a punta. Backend: conector de ListenBrainz por
username público (D37), modelo de eventos con timestamp (`NormalizedEvent` +
tabla `user_events`, migración 0004, D38), `Connector[RawT, OutT]` generalizado,
resumen con ventana temporal real —"más escuchadas en los últimos 30 días"—
(D39), refresco incremental por `min_ts` (D40, cierra D17) y tools MCP
`music.summary`/`music.top_artists`/`music.recent` + resource. Web: slice
espejo del de Juegos (hook `useSource` genérico, `MusicDetail` con alta por
username, resumen de escuchas/top artistas/top canciones, refresco y descarga
reales), Música activa en el panorama de Inicio y en Fuentes, y consultas de
música en el playground de Conectar IA. Pendiente del usuario: aplicar la
migración 0004 en Supabase.

### Fase 0 — Fundación (cerrada 2026-07-02)

Monorepo `/api` (FastAPI + FastMCP) + `/web` (Next.js) con CI completo
(ruff, mypy, pytest+cobertura; eslint, tsc, vitest, build). Supabase real con
migraciones 0001-0002 aplicadas y Email auth. Backend en Render vía blueprint
(`render.yaml`): https://ethos-api-s10w.onrender.com — `/health` y el
handshake MCP en `/mcp/` verificados en producción. Web en Vercel:
https://ethos-steel.vercel.app. Keep-alive de UptimeRobot cada 5 min.
Secretos solo en Render y `.env` local (ENCRYPTION_KEY Fernet generada,
Steam API key cargada, JWT por JWKS sin secreto legacy).
