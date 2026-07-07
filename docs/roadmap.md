# Roadmap — Contexto

Fases de construcción. Cada tarea se marca `[x]` al completarse; al cerrarse una
fase entera se mueve a `## Histórico de fases completadas` como resumen breve.

**Fases 0-4 completas**: infraestructura en producción, las cinco categorías
del catálogo (D27) activas de punta a punta y el pulido de la Fase 4 cerrado.
Sin fase activa: candidatas para la siguiente en "Pendientes".

Diferidas fuera del catálogo (D27, revisión 2026-07-03): Lugares (Swarm),
Comida (Beli) y Juegos de mesa (BoardGameGeek) — ya visibles "en desarrollo"
con aviso (D50). Retirada (D31): Actividad física — sin fuente viable.

## Pendientes y decisiones por resolver

- Categorías diferidas (Lugares, Comida, Juegos de mesa): decidir si alguna se construye ahora que hay lista de interesados (D50).
- Qué histórico incluye el contexto descargable cuando lleguen los eventos con timestamp (la forma v1 quedó fijada en D34).
- Resolución de títulos de la wishlist de Steam (D32): candidata a la caché de catálogos globales.
- Política de retención del histórico inactivo (cuánto tiempo se conserva).
- Estrategia de caché de catálogos globales (esquema de logros, metadatos de juegos, fichas de géneros D55) compartidos entre usuarios.
- El ping de keep-alive golpea `/health`, que no toca Supabase: añadir un toque de BD (o cron) para evitar su pausa a los 7 días.
- UI de revocación por cliente OAuth en Ajustes (el cliente ya puede revocar por `POST /oauth/revoke`, D61; falta la vista del usuario).
- CIMD (client_id como URL de metadata, spec MCP 2025-11) si el registro dinámico de clientes se vuelve ruidoso (D61).
- Entradas a mano en categorías sin proveedor conectado (hoy solo en el detalle conectado, D51).

## Histórico de fases completadas

### Fase 4 — Pulido y robustez (cerrada 2026-07-06)

Las diez tareas cerradas (D50-D59): aviso de categorías en desarrollo con
lista de interés (migración 0005), entradas a mano en `user_items` que
sobreviven al refresco, sugerencias/contacto reales (tabla `feedback` 0006 +
SMTP opcional), borrado de cuenta con deshacer de 30 días y job de purga
(0007), playground simulado con aviso explícito (LLM real descartado), OAuth
2.1 en el MCP (DCR + PKCE + refresh rotatorio + discovery, 0008, consentimiento
en `/oauth/autorizar`; `eth_live_` sigue vigente), géneros de juegos desde la
store de Steam (cierra D16), KMS descartado (D57), Dockerfile para Cloud Run
(D58) y objetivos de cobertura con gates en CI (api ≥88%, web por dimensión,
D59; versión 0.2.0). api 213 tests (90,3%), web 75, builds en verde.

### Fase 3 — Categorías restantes (cerrada 2026-07-05)

Catálogo completo activo, sin migraciones nuevas. Cine y TV / Trakt (D41-D44,
backend + web), Anime y manga / AniList (GraphQL público sin key, D45-D46),
Libros / Goodreads por import CSV (D47-D48) y modo import genérico con
autodetección por firma de cabeceras (`POST /imports`, D49). `profile.search`
generalizado y web des-duplicada (tarjetas/filas por descriptor, modal de
contexto y form de username compartidos). api 168 tests (93.2%), web 55, build
verde.

### Fase 2 — Música / ListenBrainz (cerrada 2026-07-04)

Segunda categoría de punta a punta, estrenando el modelo de eventos con
timestamp (`NormalizedEvent` + `user_events`, migración 0004, D37-D39),
refresco incremental por `min_ts` (D40) y tools `music.*`. Web espejo del
slice de Juegos (hook `useSource` genérico, alta por username).

### Fase 1 — Slice vertical: Juegos / Steam (cerrada 2026-07-03)

La v1 completa: conexión de Steam por OpenID con manejo de perfil privado,
conector (biblioteca, deseados D32, horas, completado top-20 D33, perfil),
normalización al contrato común, persistencia tras puerto con respaldo
Supabase (migración 0003, D35), resumen + contexto descargable (D24/D34),
refresco asíncrono con estados de frescura (D36), MCP con auth por token
`eth_live_…` (D22), tools `games.*` con métrica de KB (D28), registry (D21) y
hardening de la API (D30). Web del diseño completa (auth D26, shell, Inicio,
Detalle, Fuentes, Conectar IA, Ayuda, Ajustes, landing) cableada al API.

### Fase 0 — Fundación (cerrada 2026-07-02)

Monorepo `/api` (FastAPI + FastMCP) + `/web` (Next.js) con CI completo.
Supabase con migraciones 0001-0002 y Email auth; backend en Render
(https://ethos-api-s10w.onrender.com), web en Vercel
(https://ethos-steel.vercel.app), keep-alive de UptimeRobot y secretos solo en
Render/`.env` local. `/health` y handshake MCP verificados en producción.
