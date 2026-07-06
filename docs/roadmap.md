# Roadmap — Contexto

Fases de construcción. Cada tarea se marca `[x]` al completarse; al cerrarse una
fase entera se mueve a `## Histórico de fases completadas` como resumen breve.

Fases 0-3 completas: infraestructura en producción y las cinco categorías del
catálogo (D27) activas de punta a punta. Queda la Fase 4.

## Fase 4 — Pulido y robustez

- [x] "Avísame cuando esté lista" para categorías en desarrollo.
- [x] Entradas a mano (añadir registros sin proveedor).
- [ ] Envío real de sugerencias y contacto (persistencia + notificación).
- [ ] Borrado de cuenta con deshacer de 30 días (correo + purga diferida).
- [ ] Playground de Conectar IA con LLM real.
- [ ] Migración del auth del MCP a OAuth 2.1.
- [ ] Enriquecimiento de géneros de juegos.
- [ ] Envelope encryption con KMS (si se requiere).
- [ ] Opción de mover el backend a Cloud Run para eliminar cold starts.
- [ ] Empaquetado y distribución pulidos; objetivos de cobertura de tests.

Diferidas fuera del catálogo (D27, revisión 2026-07-03): Lugares (Swarm),
Comida (Beli) y Juegos de mesa (BoardGameGeek). Se reevaluarán ahora que las 5
están cerradas. Retirada (D31): Actividad física — sin fuente viable.

## Pendientes y decisiones por resolver

- Géneros de juegos: fuente de enriquecimiento (store API de Steam vs IGDB/RAWG). (D16)
- Qué histórico incluye el contexto descargable cuando lleguen los eventos con timestamp (la forma v1 quedó fijada en D34).
- Resolución de títulos de la wishlist de Steam (D32): candidata a la caché de catálogos globales.
- Política de retención del histórico inactivo (cuánto tiempo se conserva).
- Destino de las sugerencias (tabla + ¿aviso por correo?) y del contacto personal.
- Objetivos concretos de cobertura de tests y umbrales de CI.
- Estrategia de caché de catálogos globales (esquema de logros, metadatos de juegos) compartidos entre usuarios.
- El ping de keep-alive golpea `/health`, que no toca Supabase: añadir un toque de BD (o cron) para evitar su pausa a los 7 días.

## Histórico de fases completadas

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
