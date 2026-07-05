# ACTIVE_TASK — Fase 3: Cine y TV / Trakt (backend)

Tercera categoría sobre los puertos existentes. Cine y TV encaja en el modelo
"obra + relación" (películas y series vistas, con plays y última vez visto), así
que reutiliza el `NormalizedItem` y las tablas de Juegos, pero conectando por
username público como Música. El cableado web queda para un chunk siguiente.

### 1. Contexto y Archivos Afectados

Patrones ya establecidos: modelo item con puerto + memoria + Supabase
(`games/store.py`, `user_items`/`source_state`), conexión por username público
cifrado (`music/router.py` + credenciales, D37), refresco con
`BackgroundTasks` y estados de frescura (`sources_status.py`, D36), tools MCP
por namespace con métrica de KB (`mcp_server.py`, D28) y registro de conectores
(D21). Trakt lee datos públicos de un usuario con el `client_id` de la app en el
header `trakt-api-key` (sin OAuth), igual de barato que ListenBrainz.

Nuevos: `connectors/trakt/{client,connector}.py`, `film/{store,summary,context,
service,router,deps}.py`. Editados: `config.py` (`trakt_client_id`),
`connectors/registry.py` (registrar Trakt), `main.py` (montar router),
`mcp_server.py` (tools `film.*`). No hace falta migración: `user_items` y
`source_state` son genéricos por categoría (D35). Tests nuevos y actualización
de `test_registry.py`.

### 2. Evaluación Crítica — decisiones tomadas

Veredicto: **bueno**. La categoría encaja limpio en la infraestructura sin
tocar el esquema de datos; el único servicio externo (client_id de Trakt) es
gratis y se custodia en el servidor. Riesgo: los datos "vistos" de Trakt vienen
**agregados** (no como historial de eventos), así que el refresco reemplaza el
conjunto completo (como Juegos), no incrementa (como Música) — hay que dejarlo
explícito para no confundir el modelo con el de eventos.

Decisiones (delegadas):

- **D41 · Conexión de Cine/TV**: Trakt por **username público** + `client_id`
  del servidor en el header `trakt-api-key` (sin OAuth). El username se guarda
  como credencial cifrada del proveedor `trakt` (categoría film), como el de
  ListenBrainz (D37).
- **D42 · Modelo item (no evento)**: películas y series son `NormalizedItem`
  (obra + relación: `status=consumed`, `plays`, `last_watched_at`,
  `episodes_watched`). Reutiliza `user_items`/`source_state` con `category=film`
  — **sin migración**. Los agregados de `/users/{u}/stats` (minutos y conteos)
  se guardan en `provider_profile` (como el perfil de Steam) y alimentan los
  totales del resumen.
- **D43 · Resumen y contexto de Cine/TV**: `FilmSummary` = películas / series /
  episodios vistos, **horas totales** (de `/stats`), top películas por plays,
  top series por episodios y vistos recientes por `last_watched_at`. Contexto
  `film.context.json` con la misma información. Tools MCP `film.summary`,
  `film.top_movies`, `film.recent` (+ resource `ethos://film/summary`).
- **D44 · Refresco de Cine/TV**: refresco **completo por pasada** (watched
  movies + watched shows + stats); Trakt ya entrega lo visto agregado, así que
  `replace_items` es idempotente (como Juegos). El incremental por `/history`
  se difiere. Perfil privado o usuario inexistente (401/403/404) → estado
  `private` con guía para la web.

Deuda: sin runtime por ítem (los minutos totales salen de `/stats`, no por
película); el desglose fino de series (temporadas/episodios individuales) se
difiere. `profile.search` del MCP sigue mirando solo Juegos (se generalizará
cuando haya más categorías con la web cableada).

### 3. Plan de Acción Detallado

- [x] **Paso 1: [config.py]** `trakt_client_id: SecretStr` (secreto del servidor).
- [x] **Paso 2: [connectors/trakt/client.py]** `TraktApiClient` (headers
  `trakt-api-key`/`trakt-api-version`, throttle, `httpx` inyectable):
  `get_user_stats`, `get_watched_movies`, `get_watched_shows`; `TraktApiError`
  con `status_code`.
- [x] **Paso 3: [connectors/trakt/connector.py]** `TraktConnector`
  (id=trakt, category=film), `TraktRawData`, `TraktStats`; `normalize` de
  películas y series a `NormalizedItem` y `stats` desde `/stats`.
- [x] **Paso 4: [film/store.py]** `FilmStore` puerto + `InMemoryFilmStore` +
  `SupabaseFilmStore` (`user_items`/`source_state`, `category=film`, stats en
  `provider_profile`).
- [x] **Paso 5: [film/summary.py]** `FilmSummary` + `build_film_summary`
  (totales de stats, top películas/series, vistos recientes).
- [x] **Paso 6: [film/context.py]** `build_film_context` (`film.context.json`).
- [x] **Paso 7: [film/service.py]** `TraktApi` Protocol + `refresh_user_film`
  (fetch → normalizar → persistir; 401/403/404 → `private`, D44).
- [x] **Paso 8: [film/deps.py + film/router.py]** deps (store memoria/Supabase,
  cliente Trakt) y endpoints `POST /sources/trakt[/refresh]`, `GET /sources/film`,
  `GET /context/film`.
- [x] **Paso 9: [mcp_server.py]** tools `film.summary`, `film.top_movies`,
  `film.recent` + resource, con auth y KB servidos.
- [x] **Paso 10: [registry.py + main.py]** registrar `TraktConnector` y montar
  el router.
- [x] **Paso 11: [tests]** cliente (MockTransport), connector (golden), store
  (memoria + PostgREST simulado), summary, service (fake), router (JWT), tools
  MCP; actualizar `test_registry.py`.

### 4. Reporte de Pruebas

**[APROBADO]** — ruff y mypy sin incidencias (82 archivos); pytest 127/127 (21
nuevos: cliente Trakt, conector golden, store memoria + PostgREST simulado,
resumen, servicio con perfil privado, endpoints con JWT y tools MCP), cobertura
93.3%. Secretos: Trakt se lee por username público + `client_id` del servidor
(config cifrada, sin literales); grep limpio. Idioma D19 correcto. Sin migración
(reutiliza `user_items`/`source_state`). Pendiente del usuario: registrar la app
de Trakt y poblar `TRAKT_CLIENT_ID` en Render; el cableado web es el siguiente
chunk (por-revisar.md).
