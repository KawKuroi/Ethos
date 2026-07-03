# Estado actual — Ethos

Estado vivo del proyecto. efesto lee este documento para saber en qué fase
estamos y lo actualiza al cerrar cada tarea (entrada con fecha `AAAA-MM-DD`).

## Estado general

Fase 0 cerrada: infraestructura viva en producción (Render + Vercel +
Supabase + keep-alive). El diseño de la interfaz (Claude Design) está
terminado y es la fuente de verdad de la UI (D25, `design.md`). El trabajo
activo es la Fase 1: slice Juegos/Steam en backend y las pantallas del
diseño en `/web`.

URLs de producción: API+MCP https://ethos-api-s10w.onrender.com · web
https://ethos-steel.vercel.app

## Activo

**Fase 1 — Slice Juegos / Steam** (prácticamente cerrada). Web completa: las 8
pantallas del diseño (landing, auth, shell, Inicio, Detalle, Fuentes, Conectar
IA, Ayuda/Ajustes) con datos de ejemplo. Backend completo del slice: conector
de Steam (biblioteca, recientes, wishlist D32, completado top-20 D33, perfil),
OpenID de Steam verificado contra `check_authentication`, persistencia tras
puerto (`GamesStore`, memoria, D35), resumen + contexto descargable
(`GET /context/games`, D34), refresco con estados de frescura (D36) y MCP con
auth por token `eth_live_…` (D22) y tools `games.*` + `profile.search` con KB
servidos (D28). Respaldo Supabase implementado (migración 0003 + repos
PostgREST con selección automática por entorno, D35). **Para cerrar Fase 1
falta**: que el usuario aplique la migración 0003 en Supabase (pasos en
`por-revisar.md`) y el cableado de la web a datos reales (siguiente ciclo;
hoy la web muestra datos de ejemplo).

Fase 0 completa (2026-07-02): Supabase real con migraciones aplicadas,
servicio en Render (blueprint `render.yaml`), web en Vercel, keep-alive de
UptimeRobot y secretos poblados. `/health` y el handshake MCP verificados en
producción.

## Decisiones de inicialización

- Framework web: Next.js (App Router). Registrado como D18.
- Idioma del código: identificadores en inglés; texto humano en español.
  Registrado como D19 y detallado en `global.md`.
- Alcance del arranque: backend + infraestructura primero; `/web` después.

## Bitácora

### 2026-07-03 (Fase 1: backend · respaldo Supabase de la persistencia, D35)

- Migración `0003_games_and_mcp_tokens.sql`: tabla `user_items` (genérica por
  categoría; `payload` jsonb = `NormalizedItem`, columnas `external_id`,
  `status`, `title`, `playtime_minutes` extraídas para indexar; RLS
  owner-only), tabla `mcp_tokens` (hash SHA-256, PK por usuario = rotación por
  upsert) y `source_state` ampliada (estado `private`, `detail`,
  `provider_profile` jsonb). Cliente PostgREST mínimo (`supabase_rest.py`,
  service_role: el backend autentica por JWT y acota por user_id; RLS bloquea
  el acceso directo) e implementaciones `SupabaseCredentialRepository`,
  `SupabaseGamesStore` (mapeo fresh↔synced) y `SupabaseMcpTokenStore`.
  Selección memoria/Supabase automática por entorno en los deps. 7 tests
  nuevos (MockTransport); ruff, mypy y pytest (84, cobertura 94.6%) en verde.
  Pendiente del usuario: aplicar la migración en Supabase (por-revisar.md);
  siguiente ciclo: cablear la web a datos reales.

### 2026-07-03 (Fase 1: backend · slice Juegos/Steam completo)

- Cierre programable del backend con decisiones delegadas por el usuario
  (D32-D36): cliente de Steam con `get_wishlist` + `get_player_achievements`;
  conector normaliza wishlist (`status=wishlist`, sin títulos, D32) y anota
  `completion_pct` (presupuesto top-20 por refresco, D33); verificación OpenID
  2.0 contra Steam (`check_authentication`, campos firmados) en
  `connectors/steam/openid.py`; paquete `games/` (store tras puerto con
  memoria indexada D35, resumen tipado, contexto D34, servicio de refresco con
  estados `never/syncing/fresh/private/error` D36) y endpoints
  `POST /sources/steam` (conecta + primer refresco), `POST
  /sources/steam/refresh` (202), `GET /sources/games` y `GET /context/games`
  (descarga D24). MCP: tokens `eth_live_…` (hash SHA-256, rotación,
  `POST /mcp-token`) y tools `games.summary`, `games.top_by_hours`,
  `games.recent`, `profile.search` + resource `ethos://games/summary`, todas
  con auth (D22) y métrica de KB servidos (D28); `ping` sigue abierto.
  36 tests nuevos: ruff, mypy y pytest (77, cobertura 95.5%) en verde.
  Pendiente único de Fase 1: respaldo Supabase de los stores en memoria
  (tablas `user_credentials`/`user_games`/`mcp_tokens` + RLS) y el cableado
  de la web a datos reales, que dependen de infra.

### 2026-07-03 (Fase 1: web · Ayuda y Ajustes)

- Ayuda (`components/app/help/`) en `/app/ayuda`: FAQ en acordeón (5 del
  prototipo), carril de sugerencias (textarea + "Enviar →/Enviado ✓", efímero) y
  contacto (mailto). Ajustes (`components/app/settings/`) en `/app/ajustes`:
  Perfil (nombre, usuario, zona horaria, "Guardar ✓" efímero), Apariencia (tema
  claro/oscuro/sistema cableado de verdad a next-themes), Datos y contexto
  (cifras + enlaces a Fuentes/Conectar IA) y Zona de peligro (diálogo de
  confirmación; el borrado real —correo + deshacer 30 días— es Fase 4). 4 tests
  nuevos; tsc, eslint, vitest (35) y build en verde. Con esto queda cerrado el
  bloque de pantallas web del diseño (auth, shell, Inicio, Detalle, Fuentes,
  Conectar IA, Ayuda y Ajustes). Efímeros pendientes de backend: envío de
  sugerencias, persistencia de perfil y borrado (Fase 4).

### 2026-07-03 (Fase 1: web · Conectar IA)

- Pantalla Conectar IA (`components/app/connect/`: `connect` (client), `data`,
  css + test) en `/app/conectar-ia`: tarjeta de estado del servidor (toggle
  simulado), tarjeta de conexión (endpoint/token placeholder con copiar
  "copiado ✓"), tres pasos, y playground "Pruébalo" con lado natural (chat con
  chips de consultas de Juegos + input propio con matching simple, typing
  efímero → respuesta con items) y lado técnico "Lo que pasa por detrás" (tool
  200 OK, barra de contexto que viaja, JSON crudo). Sin LLM (v1). 3 tests
  nuevos; tsc, eslint, vitest (31) y build en verde. Pendiente del backend del
  MCP: endpoint/token/estado reales por usuario y el matching real.

### 2026-07-03 (Fase 1: web · Fuentes)

- Vista de Fuentes (`components/app/sources/`: `sources` + css + test) en
  `/app/fuentes`, derivada de `CATEGORY_DETAIL`: resumen de 4 cifras (activas ·
  expuestas por MCP · apagadas · en desarrollo), grupo Activas (Juegos, con
  salud/proveedor/modo/frescura y "Abrir →" al detalle) y grupo En desarrollo
  (las cuatro, con chip "Próximamente"); el grupo Apagadas solo aparece si las
  hubiera (ninguna en v1). 3 tests nuevos; tsc, eslint, vitest (28) y build en
  verde.

### 2026-07-03 (Fase 1: web · Detalle de categoría)

- Detalle de categoría (`components/app/category/`: `category-detail` (client),
  `data`, `context`, `sparkline`, css + test) en `/app/categoria/[slug]`. Juegos
  (conectada): back a Inicio, header con Refrescar (efímero) y Descargar
  contexto, status strip (salud · proveedor · modo · actualizado), stat band
  (hero + sparkline SVG propio + 4 stats), y Destacados/Reciente/Listas. Modal
  "Descargar contexto" con preview JSON/MCP (generado desde los datos), copiar
  ("Copiado ✓") y descargar `<slug>.context.json`. Música/Cine/Anime/Libros:
  estado "en desarrollo". El panorama de Inicio enlaza al detalle; `metaForPath`
  resuelve el título del header por slug. Datos de ejemplo del prototipo. 3 tests
  nuevos; tsc, eslint, vitest (25) y build (rutas prerenderizadas) en verde.
  Diferido: diálogo de cambio de proveedor y estado apagado/guía de import (no
  aplican en v1).

### 2026-07-03 (Fase 1: web · pantalla Inicio)

- Pantalla Inicio ("Tu perfil") del diseño dentro del shell
  (`components/app/overview/`: `overview`, `data`, `overview.module.css` +
  test): banner "Tu IA aún no está conectada" (CTA → `/app/conectar-ia`),
  sección de alertas agregadas (dirigida por `GLOBAL_ALERTS`, hoy vacía →
  oculta), stat band "El gusto en números" (4 cifras de Juegos), "Panorama · por
  actividad" (Juegos activa con barra/valor; Música, Cine y TV, Anime y manga y
  Libros como "en desarrollo") y "Actividad reciente" en timeline. Datos de
  ejemplo del prototipo en constantes (a sustituir por el backend), como la
  landing. `/app` deja de ser placeholder. 4 tests nuevos; tsc, eslint, vitest
  (22) y build en verde. Diferido: navegación al Detalle de categoría (su tarea)
  y datos reales (backend de Steam).

### 2026-07-03 (Fase 1: web · Shell de la app)

- Armazón de la app del diseño (`App Ethos.dc.html`): layout compartido bajo
  `/app` (`src/app/app/layout.tsx`) con barra lateral (`components/app/`:
  `sidebar`, `app-header`, `nav`, `nav-icons`, `screen-placeholder` +
  `app.module.css`). Nav lateral (Inicio · Fuentes · Conectar IA · Ayuda) con
  resaltado por `usePathname`, badge ámbar pulsante en "Conectar IA"
  (`mcpConnected` fijo en falso hasta la tarea de Conectar IA), footer de perfil
  + engrane → `/app/ajustes`; header sticky con título/subtítulo por pantalla.
  Rutas por pantalla como placeholders dentro del shell (`/app`, `/app/fuentes`,
  `/app/conectar-ia`, `/app/ayuda`, `/app/ajustes`); el `/app` de placeholder de
  pantalla completa pasa a Inicio dentro del shell. Segmentos en español, como
  la auth. Responsivo mínimo (aside → top bar en <820px). 3 tests nuevos
  (Vitest, `usePathname` mockeado); tsc, eslint, vitest (18) y build en verde.
  Diferido: contenido de cada pantalla (ítems propios del roadmap), estado real
  del MCP y guardas de ruta por sesión.

### 2026-07-03 (Fase 1: web · Auth, D26)

- Pantallas de autenticación del diseño (Claude Design, `Auth Ethos.dc.html`)
  cableadas a Supabase Auth: `/auth` (login/registro segmentado con correo +
  contraseña, Google y GitHub), `/auth/recuperar` (enviar enlace),
  `/auth/nueva-clave` (fijar contraseña) y `/auth/callback` (intercambio de
  código por sesión en cookies vía `@supabase/ssr`). Clientes browser/server
  perezosos (`src/lib/supabase/`), validación (correo, mínimo 8, Términos),
  mostrar/ocultar contraseña, mensajes en español y toggle de tema reutilizando
  `next-themes`. Los CTA "Abrir la app" de la landing apuntan a `/auth`. 6 tests
  nuevos (Vitest, Supabase mockeado); tsc, eslint, vitest (15) y build en verde.
  Deps `@supabase/supabase-js` + `@supabase/ssr`; `web/.env.example` con
  `NEXT_PUBLIC_SUPABASE_URL/ANON_KEY`. **Seguimiento (infra del usuario, como
  Fase 0):** habilitar los proveedores Google/GitHub en Supabase (client
  id/secret + redirect URLs) y poblar las env vars en Vercel para que el OAuth
  opere; correo+contraseña ya funciona. Diferido a la Shell: guardas de ruta y
  guardado/expiración de sesión global.

### 2026-07-03 (Fase 1: ajustes de la landing tras revisión del usuario)

- Revisión visual del usuario en producción: (1) Bricolage Grotesque ahora
  carga el eje óptico `opsz` (los titulares no se veían como el diseño);
  (2) `prefers-reduced-motion` pasa de apagarlo todo a apagar solo
  entradas/reveals, como el prototipo (con los efectos de Windows
  desactivados no se veía ninguna animación); (3) catálogo reducido a 6
  categorías — fuera Lugares, Comida y Juegos de mesa (diferidas, D27
  revisada; enum `Category` y galería a 6) y galería sin animación de
  entrada; (4) trazo del logo más visible (1.5/.95); (5) textarea de
  sugerencias sin resize.

### 2026-07-03 (Fase 1: landing pública)

- Landing implementada desde el prototipo real (`Landing mockups.dc.html`,
  copia local del proyecto de diseño en
  `D:\Programacion\Proyectos\Ethos_claude_design`): header, hero con flujo
  animado apps→Ethos→IA, "¿Qué es un MCP?" con diagrama, "Cómo se usa",
  walkthrough interactivo de Juegos (autoplay 4,2 s) + galería con las 9
  categorías (D27; el prototipo traía 7), FAQ, sugerencias ("Enviado ✓",
  envío real en Fase 4) y footer. JetBrains Mono y tokens `--code-*`
  añadidos; `/app` con placeholder para los CTA; responsividad mínima.
  9 tests (Vitest) y build estático en verde. `design.md` §4 actualizado.

### 2026-07-03 (Fase 1: hardening de la API, D30)

- Protección anti-abuso a petición del usuario: middlewares ASGI propios
  (`middleware.py`) — rate limit por IP con ventana deslizante (429 +
  Retry-After, `/health` exento), límite de tamaño de cuerpo (413) y
  cabeceras de seguridad — más CORS restringido a la web, TrustedHost y
  docs apagados en producción (`create_app()` factory). Cliente de Steam
  con throttle de intervalo mínimo (reloj/sleep inyectables). `render.yaml`
  con `--proxy-headers` y env vars ALLOWED_ORIGINS/ALLOWED_HOSTS. 10 tests
  nuevos; ruff, mypy y pytest (41, cobertura 94.6%) en verde.

### 2026-07-02 (Fase 0 cerrada: infraestructura en producción)

- Fase 0 guiada con el usuario: proyecto Supabase creado con migraciones
  0001-0002 y Email auth; `render.yaml` (blueprint) → servicio
  `ethos-api-s10w.onrender.com` con secretos en el dashboard; web en Vercel
  (`ethos-steel.vercel.app`); keep-alive de UptimeRobot a `/health`.
  `ENCRYPTION_KEY` generada directo al `.env` (sin exponerla);
  `SUPABASE_JWT_SECRET` vacío (JWKS). Verificado en producción: `/health`
  200, `/mcp/` 405 con `allow: DELETE, POST` y handshake MCP `initialize`
  correcto (un 404 inicial era el deploy propagándose). Pendiente anotado:
  `/health` no toca Supabase (pausa a los 7 días).

### 2026-07-03 (catálogo: investigación de fuentes y retiro de Actividad física)

- Investigación de viabilidad de fuentes por categoría (APIs y exports, estado
  2026). Resultado: Steam, ListenBrainz, Trakt, AniList y Goodreads (import)
  confirmados; Spotify, Letterboxd, Garmin y Fitbit descartados como API;
  Hardcover (libros) y Simkl (cine/TV) identificados como alternativas API
  reales; TV Time cierra el 2026-07-15. Actividad física retirada del catálogo
  (D31): Strava prohíbe usar datos de su API con IA y no hay alternativa
  viable. Catálogo activo a 5: enum `Category` sin `fitness`, landing y tests
  actualizados (api y web en verde), docs ajustados (prd, architecture,
  data-model, design, roadmap, D23/D27/D31). Alternativas depuradas (D27):
  fuera las inviables (Epic; Deezer/Tidal/TV Time ni entran); Juegos queda
  Steam + Xbox/PlayStation (APIs no oficiales) + GOG (import); modos por
  proveedor anotados en `architecture.md` 4.1.

### 2026-07-02 (Fase 0/1: fundación de /web)

- Creado `/web`: Next.js 16 (App Router, TS, src-dir, ESLint, sin Tailwind,
  pnpm). Fundación del diseño (D25/D29): tokens en `globals.css` (paleta slate
  clara/oscura vía `data-theme`, acentos de las 9 categorías, salud/alerta,
  radios, sombras, keyframes `ethScreen`/`spin`/`pulse`, reduced-motion),
  fuentes `next/font` (Bricolage Grotesque + Hanken Grotesk), `next-themes`
  (claro/oscuro/sistema, `ethos_theme_mode`) y placeholder. Testing: Vitest +
  Testing Library (jsdom, 3 tests). CI: job `web` (eslint, tsc, vitest,
  build). READMEs actualizados. Cierra el item de monorepo de Fase 0; el
  resto de Fase 0 (Supabase real, Render, Vercel, ping, secretos) requiere
  cuentas del usuario.

### 2026-07-02 (Fase 1: contrato generalizado + registry)

- `MediaCategory` → `Category` con los 9 ids del diseño (games, music, film,
  anime, fitness, books, places, food, board) (D27) y registro de conectores
  `connectors/registry.py` (D21): (categoría, proveedor) → clase de conector,
  duplicado → ValueError, ausente → LookupError; Steam registrado. Credenciales
  y conector de Steam sobre el enum nuevo. Tests nuevos del registry y del
  catálogo. ruff, mypy y pytest (31, cobertura 96%) en verde.

### 2026-07-02 (revisión técnica)

- Revisión del backend con quick wins aplicados: verificación de JWT con
  soporte JWKS (ES256/RS256 con caché; HS256 legacy como fallback) y claims
  obligatorios (`exp`, `sub`, `aud`, `iss` si hay URL); `SecretStr` para los
  secretos de config; pin `fastmcp>=3.4,<4` y `httpx<1`; ruff con reglas `S`
  (bandit) y `RUF`; pytest-cov con umbral 85% (hoy ~95%); helpers de JWT
  deduplicados en `tests/helpers.py` + fixtures en `conftest.py`; tests
  nuevos (token expirado / sin exp / aud incorrecta / ES256 sin URL, roundtrip
  real del tool `ping` in-memory, DELETE 404, recently_played, respuesta
  no-dict de Steam); CI con cache de uv, push solo en main y `paths-ignore`
  de docs; corregida la mención "Fernet/AES-GCM" → Fernet (AES-128-CBC+HMAC).
  Roadmap: la generalización `Category` (9) se adelanta a Fase 1. Pendientes
  anotados para sus tareas: CORS al llegar `/web`, repositorio Supabase con
  Protocol async (API con JWT del usuario vía RLS; worker con service_role),
  validación de `provider` contra el registry (D21), Polars solo cuando llegue
  el primer import grande.

### 2026-07-02

- Diseño de Claude Design revisado (app, auth y landing) y adoptado como
  fuente de verdad de la UI. Docs re-planteados: nuevo `design.md` (tokens,
  pantallas, interacciones); PRD con las dos salidas del contexto (descarga +
  MCP) y el concepto "panel" (sustituye a "dump"); catálogo fijado en 9
  categorías con estados y despliegue secuencial —una por una, probada y
  confirmada antes de la siguiente; en la v1 solo Juegos activa y el resto
  "en desarrollo"; Pódcasts y YouTube del prototipo quedan fuera—; auth de la
  app = correo + Google + GitHub (Steam OpenID queda solo como conexión de
  fuente); tools del MCP con namespace (`games.top_by_hours`…) y métrica de
  KB servidos; web sin Recharts (tokens CSS + CSS Modules + SVG propio).
  Decisiones D24-D29; roadmap con la implementación del diseño en Fase 1 y
  pulido en Fase 4.

### 2026-06-30

- Backend de credenciales de usuario (D20): migración `0002_user_credentials.sql`
  (tabla + RLS owner-only), cifrado Fernet (`security.py`), verificación de JWT de
  Supabase (`auth.py`) y endpoints `/credentials` (conectar/listar/desconectar)
  sobre repositorio en memoria. Deps `cryptography` y `pyjwt`. ruff, mypy y
  pytest (17) en verde. Pendiente: repositorio respaldado por Supabase y su
  estrategia RLS. Confirmado: Steam sigue con OpenID + key del servidor (D12).

### 2026-06-29

- Documentación de contexto adaptada a efesto: añadidos `global.md` (reglas
  invariables, convención de idioma) y `current.md` (este archivo); `roadmap.md`
  convertido a checkboxes con sección de histórico; decisiones D18-D19 añadidas.
- Repositorio remoto creado en GitHub (`KawKuroi/Ethos`). Git local pendiente de
  inicializar y conectar.
- Andamiaje de Fase 0 (backend + infra): creado `/api` (FastAPI + FastMCP, un
  solo servicio con `/health` y `/mcp`, tool `ping`, tests), `/supabase`
  (migración `0001_foundation.sql` con `profiles`, `source_state`, índices,
  triggers y RLS owner-only), CI (`.github/workflows/ci.yml`), `.gitignore` y
  `.env.example`. Verificado en local: ruff, mypy y pytest en verde. Eliminado
  `design-brief.md` (no lo usa efesto). README del proyecto actualizado.
- Fase 1 (backend, parte 1): contrato normalizado (`schema.py`), interfaz de
  conector (`connectors/base.py`) y conector de Steam (`connectors/steam/`:
  cliente HTTP con httpx + normalización de biblioteca, jugados recientes y
  perfil). Tests de fixtures (golden-file) y `httpx.MockTransport`. `httpx`
  pasó a dependencia de runtime. ruff, mypy y pytest (8) en verde.
- Revisión de seguridad + planificación: auditado `/api` y `/supabase` (sin
  vulnerabilidad activa: sin secretos hardcodeados, RLS owner-only, timeouts, sin
  fuga de la API key). Planificado: sesión + credenciales cifradas
  (`user_credentials`, D20), registro de conectores (D21), guardrail de auth del
  MCP (D22) y catálogo de 9 categorías con generalización del contrato (D23).
  Docs actualizados (architecture, data-model, decisions, roadmap).
