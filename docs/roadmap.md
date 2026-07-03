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
- [ ] Respaldo Supabase de los repositorios en memoria: tablas `user_credentials`, `user_games` y `mcp_tokens` con RLS. (D20/D35 — único pendiente del backend; requiere infra)
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
- [x] Tests de todas las capas pasando en CI. (api: 77, cobertura 95%; web: 35)

## Fase 2 — Segunda categoría: Música / ListenBrainz

- [ ] Conector de ListenBrainz por API (listens con timestamp).
- [ ] Estrena la consulta temporal real ("más escuchadas en los últimos 30 días").
- [ ] Modelo de eventos con timestamp y sus índices.
- [ ] Tools del MCP para música (`music.*`: artistas, álbumes, tracks, ventanas temporales).
- [ ] Música sale de "en desarrollo" y queda activa en la web (el detalle por categoría ya es genérico).

## Fase 3 — Categorías restantes (secuencial, D27)

Una categoría a la vez: construir, probar y confirmar antes de empezar la
siguiente; al activarse sale de "en desarrollo". Orden tentativo (proveedor
inicial; alternativas según D4/D6/D27):

- [ ] Cine y TV: Trakt (API). Alternativa: Letterboxd (import).
- [ ] Anime y manga: AniList (API).
- [ ] Libros: Goodreads (import). Alternativas: StoryGraph (import), Hardcover (API).
- [ ] Modo import genérico con autodetección de archivo y guías por proveedor.

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

### Fase 0 — Fundación (cerrada 2026-07-02)

Monorepo `/api` (FastAPI + FastMCP) + `/web` (Next.js) con CI completo
(ruff, mypy, pytest+cobertura; eslint, tsc, vitest, build). Supabase real con
migraciones 0001-0002 aplicadas y Email auth. Backend en Render vía blueprint
(`render.yaml`): https://ethos-api-s10w.onrender.com — `/health` y el
handshake MCP en `/mcp/` verificados en producción. Web en Vercel:
https://ethos-steel.vercel.app. Keep-alive de UptimeRobot cada 5 min.
Secretos solo en Render y `.env` local (ENCRYPTION_KEY Fernet generada,
Steam API key cargada, JWT por JWKS sin secreto legacy).
