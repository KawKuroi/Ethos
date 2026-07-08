# Estado actual — Ethos

Estado vivo del proyecto. efesto lee este documento para saber en qué fase
estamos y lo actualiza al cerrar cada tarea (entrada con fecha `AAAA-MM-DD`).

## Estado general

**Fases 0-4 completas a nivel de código.** Infraestructura viva en producción
(Render + Vercel + Supabase + keep-alive); las cinco categorías del catálogo
de punta a punta (Fases 1-3); y el pulido de la Fase 4 (D50-D59): aviso de
categorías en desarrollo, entradas a mano, sugerencias y borrado de cuenta
reales, OAuth 2.1 en el MCP, géneros de juegos, Dockerfile para Cloud Run y
gates de cobertura en CI (versión 0.2.0). Migraciones 0001-0008 aplicadas
(2026-07-07). Pendiente de activación en producción por el usuario: env vars
(`TRAKT_CLIENT_ID`, `PUBLIC_BASE_URL`, `WEB_BASE_URL`, SMTP opcionales), job
de purga y verificación e2e — ver `por-revisar.md`. Sin fase activa:
candidatas en los pendientes del roadmap.

URLs de producción: API+MCP https://ethos-api-s10w.onrender.com · web
https://ethos-steel.vercel.app

## Activo

**Pulido de UI (2026-07-07).** Spinners y badges vuelven a animarse
(keyframes locales por módulo: CSS Modules hasheaba los globales), el tema se
cambia solo desde Ajustes (aplica a landing + app), el perfil usa el nombre
real de Supabase Auth (editable en Ajustes; fuera Usuario y Zona horaria),
favicon.ico regenerado con el logo constelación (el viejo triángulo seguía
desplegado) y glifo ampliado en icon.svg/apple-icon, el logo del panel enlaza
a la landing, el formulario de la landing pide solo la sugerencia y la
tarjeta "¿Algo más personal?" se elimina (correo inventado).

**Compatibilidad del MCP con conectores online (2026-07-07, D61).** El
authorization server acepta redirect_uri de loopback con puerto efímero
(RFC 8252), sirve los aliases de discovery que prueban los clientes MCP,
anuncia `offline_access` (los conectores conservan el refresh token) y añade
`POST /oauth/revoke` (RFC 7009). Con esto el MCP queda conectable desde
Claude.ai (conector personalizado), Claude Code y cualquier cliente MCP
remoto con OAuth estándar.

**Historial completo en los contextos (2026-07-07, D60).** Los contextos
descargables y el MCP (tools `<cat>.history` nuevas) sirven el detalle
completo de cada categoría con límite claro (1000 entradas) y metadatos de
uso (`usage_pct`, `truncated`); el modal de la web muestra el uso del límite,
avisa al alcanzarlo y corrige su centrado (portal sobre `<body>`).

**Fase 4 cerrada (2026-07-06).** Las diez tareas completadas con commit por
tarea (D50-D59); resumen en el histórico del roadmap. Siguiente fase por
decidir (candidatas en los pendientes del roadmap: categorías diferidas con
lista de interesados, caché de catálogos globales, retención del histórico).
Pendiente del usuario para producción: migraciones 0005-0008, env vars nuevas
del blueprint y verificaciones — ver `por-revisar.md`.

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

### 2026-07-07 (pulido de UI: carga, tema, perfil, iconos y formularios)

- Bug real de CSS Modules corregido: `animation: spin/pulse` referenciaba
  keyframes de `globals.css`, pero CSS Modules localiza el nombre y la
  animación nunca corría (el spinner del login no giraba). Keyframes locales
  en `auth/category/sources/connect/overview/app.module.css`.
- Tema único desde Ajustes: `ThemeToggle` eliminado de landing y pantallas de
  auth (el `ThemeProvider` raíz ya hace global la elección); copy de
  Apariencia aclarado.
- Perfil real: hook `lib/use-user.ts` (sesión de Supabase, `full_name`/`name`
  de `user_metadata`, actualizado por `onAuthStateChange`); sidebar muestra
  nombre, correo e inicial reales y su logo enlaza a `/`; Ajustes deja solo
  Nombre (guardado real con `auth.updateUser`) + Correo en solo lectura;
  fuera Usuario y Zona horaria (las fechas ya usan la zona del navegador).
- Iconos: `favicon.ico` regenerado con el logo constelación —el desplegado
  era el triángulo del bootstrap— (script PIL, 16/32/48/256); glifo ampliado
  en `icon.svg` (scale 1.68) y `apple-icon.tsx` (148×131).
- Formularios: sugerencias de la landing solo con el textarea (sin
  nombre/correo); tarjeta "¿Algo más personal?" de Ayuda eliminada (el
  `mailto:hola@ethos.app` era un placeholder sin canal real).
- `coverage/` añadido a los ignores de eslint (el reporte generado disparaba
  un warning local). web 81 tests, gates de cobertura, tsc, eslint y build en
  verde.

### 2026-07-07 (compatibilidad del MCP con conectores online, D61)

- Revisión del sistema de conexión MCP contra los requisitos de los conectores
  remotos (docs de Anthropic + spec MCP). Huecos corregidos: redirect_uri de
  loopback ignorando el puerto (RFC 8252 — el match exacto rompía a Claude
  Code), aliases de discovery (`oauth-authorization-server/mcp`,
  `openid-configuration`), `offline_access` en `scopes_supported` (sin él los
  conectores descartan el refresh token), refresh sin `scope` (RFC 6749 §5.1)
  y revocación RFC 7009 (`POST /oauth/revoke` + `revocation_endpoint`).
  Verificado: `/mcp` responde con y sin barra final. Sin CORS para `/mcp`
  (conexión servidor-a-servidor). api 222 tests (90,1%) en verde.

### 2026-07-07 (historial completo en los contextos, D60)

- Los contextos dejan de ser solo el resumen: `history` con el detalle
  completo (items/listens, del más reciente al más antiguo) hasta 1000
  entradas (`context_history.py` compartido), con metadatos de uso (`limit`,
  `total`, `included`, `usage_pct`, `truncated`, `note`). MCP: tools nuevas
  `games/music/film/anime/books.history` (param `limit`); `kb_total` (D28)
  referencia el contexto completo. Web: indicador de uso del límite en el
  modal (barra + texto, ámbar al alcanzarlo) y fix de centrado del modal
  (portal sobre `<body>`; el transform residual de `.eth-screen` anclaba el
  `fixed` al contenido). api 218 tests (90,1%); web 78 tests, tsc, eslint y
  build en verde.

### 2026-07-06 (Fase 4 cerrada · cobertura y empaquetado, D59)

- Última tarea de la fase. Gates de cobertura que bloquean el CI: api ≥88%
  (`--cov-fail-under=88`; real 90,3%) y web por dimensión sobre todo `src`
  (`@vitest/coverage-v8`, thresholds 53/60/52/56; real 57,0/63,5/55,4/59,7),
  con `pnpm test` corriendo siempre con cobertura. Versión 0.2.0 en api y web
  como corte de la fase; línea del contenedor en el README. La Fase 4 pasa al
  histórico del roadmap; pendientes nuevos anotados (revocación OAuth por
  cliente, entradas a mano sin proveedor conectado, diferidas con lista de
  interesados).

### 2026-07-06 (Fase 4 · vía Cloud Run lista, D58)

- `api/Dockerfile` (python 3.12-slim + uv, lock congelado, PORT de plataforma,
  proxy-headers) + `.dockerignore`: el mismo servicio se despliega en Cloud Run
  u otro host de contenedores sin cambiar código. Render sigue igual;
  `render.yaml` completado con las env vars de la Fase 4 (PUBLIC_BASE_URL,
  WEB_BASE_URL, TRAKT_CLIENT_ID, SMTP opcionales). Build local pendiente de
  verificar (daemon de Docker apagado) — por-revisar.

### 2026-07-06 (Fase 4 · KMS descartado por ahora, D57)

- La condición "si se requiere" no se cumple: Fernet a nivel de app con la
  llave en el secret manager cubre la amenaza real (fuga de BD sin exponer
  credenciales) y un KMS rompería el objetivo de 0 USD/mes. Criterios de
  disparo documentados en D57 (multi-tenant serio, rotación por incidente,
  cumplimiento). Sin código.

### 2026-07-06 (Fase 4 · OAuth 2.1 en el MCP, D56)

- Authorization server mínimo integrado en el API según el patrón del spec
  MCP: discovery RFC 8414/9728, DCR RFC 7591 (clientes públicos), authorization
  code + PKCE S256 obligatorio, token endpoint con refresh rotatorio. Tokens
  `eth_oauth_`/`eth_refresh_` como hash en `oauth_tokens` (migración 0008);
  codes en memoria (10 min, un solo uso). `/mcp` responde 401 +
  `WWW-Authenticate` sin Bearer válido; `eth_live_` sigue vigente
  (`resolve_bearer_user` único). Config `PUBLIC_BASE_URL`/`WEB_BASE_URL`.
- Web: página de consentimiento `/oauth/autorizar` (sesión de Supabase,
  autorizar/denegar, redirección al cliente) + `approveOAuth` en `lib/api.ts`.
- Fix de suite: reset del rate limit entre tests (la IP compartida del
  TestClient superaba 120/min con la suite crecida). api 213 tests (90,3%),
  web 75 tests, build en verde (ruta `/oauth/autorizar` prerenderizada).

### 2026-07-06 (Fase 4 · géneros de juegos desde la store de Steam, D55)

- Cierra el pendiente D16: los géneros se enriquecen desde la ficha pública de
  la store (sin key), con presupuesto top-20 por refresco (como el completado
  D33) y degradación silenciosa por juego. `work.extra["genres"]`, `genres` en
  cada TopGame y agregado `top_genres` en resumen/contexto/MCP. Web: géneros en
  el sub del top y chips "Géneros dominantes". api 203 tests (91,3%), web 71.

### 2026-07-06 (Fase 4 · playground simulado con aviso, D54)

- El playground de Conectar IA se queda simulado (LLM real descartado: costo y
  abuso). Se añade el aviso "Demostración con datos de ejemplo — no consulta tu
  perfil real ni usa un modelo de IA" y se corrige el copy del chat que decía
  "consulto tus fuentes conectadas". Test del aviso. web 71 tests.

### 2026-07-06 (Fase 4 · borrado de cuenta con deshacer de 30 días, D53)

- Zona de peligro de Ajustes real. Backend: módulo `account/` (service con
  wipe/schedule/status/cancel/purge, mailer de aviso, auth_admin GoTrue, deps
  503 sin Supabase, router `/account/*`), migración 0007 (`account_deletions`),
  `CurrentUserEmail` en auth.py, job `python -m ethos_api.account.purge_job`
  para el cron. 9 tests nuevos. api 201 tests, 91.3%.
- Web: ops de cuenta en `lib/api.ts`; Ajustes cablea "Eliminar datos" y
  "Eliminar cuenta" (banner con fecha de purga + "Deshacer", estado cargado al
  entrar). Tests de Settings reescritos (4). web 70 tests, build en verde.

### 2026-07-06 (Fase 4 · sugerencias y contacto reales, D52)

- Los formularios de sugerencias (landing y Ayuda) persisten de verdad. Backend:
  módulo `feedback/` (models, repository memoria+Supabase, mailer SMTP stdlib,
  router `POST /feedback` público con `user_id` opcional), migración 0006
  (`feedback`, RLS sin políticas públicas), config SMTP (todo vacío por defecto
  → sin aviso, solo persiste). Aviso al admin best-effort en `BackgroundTasks`.
  8 tests nuevos. api 192 tests, 92.6%.
- Web: `submitFeedback` en `lib/api.ts`; landing `Suggestions` y `Help` cableados
  (estados enviando/enviado/error). El contacto personal sigue siendo el
  `mailto:` del diseño. Tests de ambos formularios actualizados. web 68 tests.

### 2026-07-06 (Fase 4 · entradas a mano, D51)

- Registros añadidos a mano (sin proveedor) en games/film/anime/books. Viven en
  `user_items` con `source="manual"` y `external_id` `manual:<uuid>`: cuentan en
  resúmenes, contexto y MCP sin código extra, y el refresco los conserva
  (`replace_items` acota su borrado; en memoria `keep_manual`).
- Backend: módulo `items/` (support, models, service, router) con
  `POST /items`, `GET /items/{category}`, `DELETE /items/{category}/{id}`;
  `add_item`/`delete_item` y refresco seguro en los cuatro stores de item.
  10 tests nuevos. api 184 tests, 92.6%.
- Web: `ManualEntries` (añadir/listar/borrar) en el detalle conectado de las
  cuatro categorías + ops en `lib/api.ts`; recarga el resumen al cambiar. web
  67 tests, tsc/eslint/build en verde.

### 2026-07-05 (Fase 4 · aviso de categorías en desarrollo, D50)

- Primera tarea de la Fase 4. Las categorías diferidas (Lugares/Swarm,
  Comida/Beli, Juegos de mesa/BoardGameGeek) vuelven a la UI como "en
  desarrollo" con formulario "Avísame cuando esté lista".
- Backend: migración 0005 (`category_interest`, RLS sin políticas públicas),
  slice `interest/` (modelos, repositorio memoria+Supabase, endpoint público
  `POST /category-interest`), `get_optional_user_id` en `auth.py` (asocia el
  usuario si hay JWT, anónimo si no), `email-validator` como dependencia
  explícita. 6 tests nuevos (anónimo, con sesión, dedupe, categoría activa
  rechazada, correo inválido, token inválido ignorado). api 174 tests, 93.0%.
- Web: `NotifyForm` compartido, `registerCategoryInterest` en `lib/api.ts`
  (adjunta el token solo si hay sesión), bloque "En camino" en la landing,
  entradas soon en `category/data.ts` (rutas `places/food/board`), pantalla
  soon con aviso y correo prellenado de la sesión, filas soon en el panorama y
  Fuentes. Tests de landing/sources/category-detail actualizados a D50 + test
  de `NotifyForm`. web 64 tests, tsc/eslint/build en verde.

### 2026-07-05 (Fase 3 cerrada: Cine/TV web + AniList + Goodreads + import genérico)

- Cierre de la Fase 3 en una sola tarea, con revisión previa del código de
  Fases 0-3 (sin bugs activos; hallazgos = duplicación web y `profile.search`
  desactualizado, corregidos aquí). Backend: conector de AniList (GraphQL
  público por username, sin key, D45; dedupe de listas personalizadas, score
  POINT_100, status→vocabulario común, D46) con slice `anime/` completo;
  conector de Goodreads (parseo del export CSV con stdlib, shelf→status,
  ISBN limpio, D47) con slice `books/` e import síncrono que reemplaza por
  subida; import genérico `POST /imports` con autodetección por firma de
  cabeceras y 422 con guía (D49); límite de cuerpo propio para rutas de
  import (`max_import_bytes`, 5 MB) sin aflojar el general; tools MCP
  `anime.*` y `books.*` + resources; `profile.search` generalizado a las
  categorías de obra con métrica de KB agregada. Web: `FilmDetail`,
  `AnimeDetail` y `BooksDetail` con datos reales; form de username y modal
  de contexto compartidos (`connect-username.tsx`, `context-modal.tsx`);
  `lib/api.ts` con operaciones de las tres categorías, contexto genérico por
  slug y errores con `detail` legible; Inicio y Fuentes generalizados por
  descriptor (`use-active-sources.ts`: una fila/tarjeta única por estado, 5
  fuentes); panel de import con guía de Goodreads; playground con consultas
  de las cinco categorías y enrutado actualizado. api: ruff/mypy/pytest 168
  (cobertura 93.2%); web: tsc/eslint/vitest 55 y build (5 rutas de categoría
  prerenderizadas) en verde. **Fase 3 cerrada**; pendiente del usuario:
  `TRAKT_CLIENT_ID` y verificación e2e en producción.

### 2026-07-05 (Fase 3: backend de Cine y TV / Trakt)

- Tercera categoría sobre los puertos existentes (D41-D44). Cliente de Trakt
  (`connectors/trakt/client.py`: `client_id` en header `trakt-api-key`, sin
  OAuth, throttle, httpx inyectable; `TraktApiError` con `status_code`) y
  conector que normaliza películas y series vistas a `NormalizedItem`
  (status=consumed, plays, last_watched_at, episodes_watched) y extrae los
  agregados de `/stats` (`TraktStats`). Slice `film/`: store item tras puerto
  (memoria + `SupabaseFilmStore` sobre `user_items`/`source_state`,
  `category=film`, stats en `provider_profile`, **sin migración**), resumen
  (películas/series/episodios vistos, horas totales, top películas por plays,
  top series por episodios, vistos recientes) y refresco completo por pasada
  (perfil privado/usuario inexistente → `private`). Endpoints `POST
  /sources/trakt[/refresh]`, `GET /sources/film`, `GET /context/film`. MCP:
  tools `film.summary`, `film.top_movies`, `film.recent` + resource. Trakt
  registrado en el registry; `trakt_client_id` en config. 21 tests nuevos;
  ruff, mypy y pytest (127, cobertura 93%) en verde. Falta el cableado web
  (Cine y TV activa) y registrar la app de Trakt con `TRAKT_CLIENT_ID`.

### 2026-07-04 (Fase 2: cableado web de Música — cierre de la fase)

- Música sale de "en desarrollo" y queda activa en la web, consumiendo el
  backend ya construido. `lib/api.ts` gana los tipos y operaciones de música
  (`getMusicSource`, `connectListenBrainz`, `refreshListenBrainz`,
  descarga/preview de `/context/music`). Se extrae un hook genérico
  `useSource<T>`; `useGamesSource` pasa a envolverlo (misma forma de retorno) y
  se añade `useMusicSource`. `MusicDetail` (espejo de `GamesDetail`, mismo
  `category.module.css`) maneja loading/error, alta por username público
  (`connect-listenbrainz.tsx`, sin OpenID, D37), estado sincronizando y vista
  conectada (hero de escuchas, top artistas y top canciones de la ventana,
  refrescar y modal de descarga reales). Inicio muestra a Música como fila
  activa del panorama (con escuchas) y su meta cuenta las fuentes activas;
  Fuentes lista Juegos y Música en Activas con recuentos por grupo; Conectar IA
  añade la consulta `music.top_artists` al playground y enruta texto de música.
  4 tests nuevos (music-detail + enrutado); tsc, eslint, vitest (42) y build en
  verde (`/app/categoria/music` prerenderizada). Con esto **Fase 2 queda
  completa a nivel de código**. Pendiente del usuario: migración 0004 y
  verificación en producción.

### 2026-07-04 (Fase 2: backend de Música / ListenBrainz)

- Segunda categoría sobre los puertos de Fase 1, estrenando el modelo de
  eventos con timestamp (D37-D40). Contrato `NormalizedEvent` y `Connector`
  generalizado a `Connector[RawT, OutT]` (Steam da items, ListenBrainz da
  eventos). Cliente de ListenBrainz (`get_listens` con `min_ts`, throttle) y
  conector que normaliza listens (artist/track/release + occurred_at,
  descartando los vacíos). Slice `music/`: event store tras puerto (memoria +
  `SupabaseEventStore` sobre `user_events`, migración 0004), resumen con
  ventana temporal de 30 días (total, ventana, top artistas, top tracks),
  refresco incremental por `min_ts` (D40) y endpoints `POST
  /sources/listenbrainz[/refresh]`, `GET /sources/music`, `GET /context/music`.
  MCP: tools `music.summary`, `music.top_artists`, `music.recent` + resource,
  con auth y KB servidos. Estado de frescura extraído a `sources_status.py`
  (compartido con Juegos). ListenBrainz registrado en el registry. 22 tests
  nuevos; ruff, mypy y pytest (106, cobertura 94%) en verde. Falta el cableado
  de la web (Música activa) y aplicar la migración 0004 en Supabase.

### 2026-07-03 (Fase 1: cableado web ↔ API — cierre del slice)

- Las pantallas dejan los datos de ejemplo y leen del backend con la sesión de
  Supabase. API: `GET /sources/games` ahora incluye el resumen
  (`GamesSummary | null`) y `GET /sources/steam/login` devuelve la URL de
  OpenID. Web: cliente `lib/api.ts` (Bearer del `access_token`), hook
  `useGamesSource`, flujo de conexión de Steam (`connect-steam.tsx` +
  `/app/steam/return`). Inicio (stat band, panorama y actividad reales),
  Fuentes (Juegos activa/apagada/private con CTA Conectar Steam), Detalle de
  Juegos (status strip, stat band sin sparkline —no hay serie en v1—, top,
  reciente, deseados, refrescar y descargar reales) y Conectar IA (endpoint
  construido + token generado bajo demanda con `/mcp-token`; el playground
  sigue simulado). Las categorías en desarrollo siguen con constantes. API
  86 tests; web 38 (mockean `lib/api`); ruff, mypy, tsc, eslint y build en
  verde. **Fase 1 queda completa a nivel de código.** Pendiente del usuario:
  `NEXT_PUBLIC_API_URL` en Vercel y la verificación real en producción.

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
