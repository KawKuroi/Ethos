# ACTIVE_TASK — Fase 3 completa: revisión + Cine/TV web + AniList + Goodreads + import genérico

Cierre de la Fase 3 en una sola tarea: revisión del código existente (Fases
0-3, secciones de `por-revisar.md`), cableado web de Cine y TV, categoría
Anime y manga (AniList), categoría Libros (Goodreads por import) y el modo
import genérico con autodetección. Pedido explícito del usuario.

### 1. Contexto y Archivos Afectados

Patrones establecidos que se replican: slice item tras puerto (`film/*`,
`user_items`/`source_state`, sin migración, D42), conexión por username
público cifrado (D37/D41), refresco con BackgroundTasks y frescura (D36),
tools MCP con métrica de KB (D28), registry (D21). En la web: `useSource<T>`,
detalle espejo (`music-detail.tsx`), alta por username, panorama/fuentes.

Línea base verificada: api 127 tests (cobertura 93.3%), web 42 tests; ruff,
mypy, tsc, eslint en verde.

Backend nuevo: `connectors/anilist/{client,connector}.py`,
`connectors/goodreads/connector.py`, `anime/{store,summary,context,service,
router,deps}.py`, `books/{store,summary,context,router,deps}.py`,
`imports/detection.py` + router. Editados: `registry.py`, `main.py`,
`mcp_server.py` (tools `anime.*`, `books.*`, `profile.search` generalizado),
`middleware.py` (límite de cuerpo mayor para rutas de import), `config.py`.
Web nuevo: `film-detail.tsx`, `anime-detail.tsx`, `books-detail.tsx`,
`connect-username.tsx` (genérico), `import-panel.tsx`, `use-film-source.ts` y
hooks espejo. Editados: `lib/api.ts`, `category/data.ts`, página de categoría,
`sources.tsx` y `overview.tsx` (generalizados por descriptor), `connect/data.ts`.

### 2. Evaluación Crítica

Veredicto: **bueno**. Las tres categorías encajan en la infraestructura sin
migraciones (`user_items`/`source_state` son genéricas por categoría). AniList
es GraphQL público por username sin key (más barato aún que Trakt); Goodreads
no tiene API y su export CSV es el caso canónico del modo import.

Hallazgos de la revisión (se corrigen en esta tarea):

- **Duplicación creciente en la web**: `sources.tsx` y `overview.tsx` tienen
  componentes casi idénticos por categoría (GamesLiveCard/MusicLiveCard,
  GamesRow/MusicRow…). Con 5 activas sería inmanejable → se generalizan con un
  descriptor por categoría (métrica hero + estado) y componentes únicos.
- **Duplicación en `lib/api.ts`**: descarga/preview de contexto repetidas por
  categoría → helpers genéricos por slug.
- **Modal de descarga duplicado**: `games-detail` y `music-detail` copian el
  mismo `DownloadModal` → se extrae uno compartido parametrizado.
- **`profile.search` desactualizado**: solo mira Juegos y su hint dice "solo
  Juegos está activa en la v1" → se generaliza a los stores de items (games,
  film, anime, books) ahora que la fase los activa.
- **`missQuery` del playground** dice "Juegos y Música" → se actualiza con las
  cinco categorías.
- Backend de Fases 0-3 revisado (auth JWKS, mcp_auth, middleware ASGI,
  supabase_rest, slices games/music/film, conectores): sin bugs activos ni
  problemas de seguridad; secciones de `por-revisar.md` cubiertas por código y
  tests correctos — lo pendiente ahí es infraestructura del usuario (env vars,
  OAuth de Supabase, migraciones), no código.

Riesgos: (1) el límite global de cuerpo (64 KB) bloquearía un export de
Goodreads → límite propio para rutas de import, sin aflojar el resto; (2) los
datos de AniList llegan agregados por lista (no eventos) → modelo item con
refresco completo idempotente, como Trakt (D44); (3) parsear CSV con la
stdlib (sin Polars): el export de Goodreads es pequeño (cientos de filas);
Polars entra cuando haya un import grande (nota previa en bitácora).

Decisiones (delegadas):

- **D45 · Conexión de Anime y manga**: AniList por **username público** vía
  GraphQL (`graphql.anilist.co`, sin key ni OAuth). Username cifrado como
  credencial del proveedor `anilist` (categoría anime), como D37/D41. Listas
  privadas o usuario inexistente (404) → estado `private`.
- **D46 · Modelo y resumen de Anime**: items (`NormalizedItem`) con
  `media_type` anime/manga en `extra`; status de AniList → vocabulario común
  (COMPLETED→consumed, CURRENT/REPEATING/PAUSED→in_progress,
  PLANNING→wishlist, DROPPED→abandoned); score normalizado 0-100;
  `engagement` = episodios/capítulos de progreso. Resumen: vistos/leídos,
  episodios, capítulos, nota media, top por nota y "en curso". Tools
  `anime.summary`, `anime.top_rated`, `anime.current` + resource.
- **D47 · Libros por import de Goodreads**: el export CSV viaja como texto
  (`text/csv`) a `POST /sources/goodreads/import`; el conector
  (`ingest_mode=import`) parsea con la stdlib y normaliza shelf→status
  (read→consumed, currently-reading→in_progress, to-read→wishlist), rating
  0-5→0-100, páginas/fechas/autor. Reemplazo completo por subida (el
  "refresco" de un import es re-subir). Límite de cuerpo propio para
  `/sources/*/import` e `/imports` (`max_import_bytes`, 5 MB).
- **D48 · Resumen de Libros**: leídos, páginas leídas, en curso (títulos),
  por leer, top autores por libros leídos y lecturas recientes por fecha.
  Tools `books.summary`, `books.currently_reading`, `books.top_authors` +
  resource.
- **D49 · Import genérico con autodetección**: `POST /imports` detecta el
  proveedor por la firma del archivo (cabeceras del CSV; v1: Goodreads) y
  delega en su flujo; desconocido → 422 con guía. La web ofrece el panel de
  import con guía por proveedor (v1: Goodreads) y estructura para añadir más.

Deuda prevista: AniList pagina `MediaListCollection` por chunks solo en listas
enormes (v1 lee la colección completa en una llamada; suficiente para el caso
real); el desglose por relecturas de Goodreads (`Read Count`) queda en
engagement sin resumen propio; sparkline del detalle sigue sin serie temporal
(no hay histórico por categoría aún).

### 3. Plan de Acción Detallado

Bloque A — Cine y TV en la web:

- [x] **Paso A1: [web/lib/api.ts]** Tipos `FilmSummary`/`FilmSource` +
  `getFilmSource`, `connectTrakt`, `refreshTrakt`; helpers genéricos
  `downloadContext(slug)`/`getContextText(slug)` y migración de juegos/música.
- [x] **Paso A2: [web/lib/use-film-source.ts]** Hook espejo con `useSource`.
- [x] **Paso A3: [web/components/app/connect-username.tsx]** Form genérico de
  alta por username (usado por música, film y anime); `connect-listenbrainz`
  pasa a envolverlo.
- [x] **Paso A4: [web/components/app/category/context-modal.tsx]** Modal de
  descarga compartido; `games-detail` y `music-detail` lo adoptan.
- [x] **Paso A5: [web/components/app/category/film-detail.tsx]** Detalle de
  Cine y TV (hero horas, stats películas/series/episodios, top películas, top
  series, vistos recientes; estados connect/syncing/private/error) + test.
- [x] **Paso A6: [category/data.ts + página categoría]** `film` pasa a `live`
  y enruta a `FilmDetail`.
- [x] **Paso A7: [sources.tsx + overview.tsx]** Generalización por descriptor
  (una tarjeta/fila genérica por categoría activa) incluyendo film.
- [x] **Paso A8: [connect/data.ts]** Consulta `film.top_movies` en el
  playground + enrutado de texto de cine/series + `missQuery` actualizado.

Bloque B — Anime y manga (AniList):

- [x] **Paso B1: [connectors/anilist/client.py]** `AniListApiClient`
  (GraphQL POST, throttle, httpx inyectable), `get_media_lists(user_name)`
  para ANIME y MANGA; `AniListApiError` con `status_code`.
- [x] **Paso B2: [connectors/anilist/connector.py]** `AniListConnector`
  (id=anilist, category=anime), `AniListRawData`; normalización D46.
- [x] **Paso B3: [anime/store.py]** Puerto + memoria + Supabase
  (`user_items`, `category=anime`, sin stats de proveedor).
- [x] **Paso B4: [anime/summary.py + anime/context.py]** `AnimeSummary` D46 y
  `anime.context.json`.
- [x] **Paso B5: [anime/service.py + deps.py + router.py]** Refresco completo
  (404→private) y endpoints `POST /sources/anilist[/refresh]`,
  `GET /sources/anime`, `GET /context/anime`.
- [x] **Paso B6: [mcp_server.py + registry.py + main.py]** Tools `anime.*` +
  resource; registrar conector y montar router.
- [x] **Paso B7: [tests anime]** Cliente (MockTransport), conector (golden),
  store, resumen, servicio (private), endpoints, tools; `test_registry.py`.
- [x] **Paso B8: [web]** `AnimeDetail` + hook + api ops + activación en
  data/página/sources/overview/playground + test.

Bloque C — Libros (Goodreads import):

- [x] **Paso C1: [config.py + middleware.py]** `max_import_bytes` y límite de
  cuerpo por ruta de import (`/imports`, `/sources/*/import`) + tests.
- [x] **Paso C2: [connectors/goodreads/connector.py]** `GoodreadsConnector`
  (`ingest_mode=import`), parseo CSV D47 con validación de columnas.
- [x] **Paso C3: [books/store.py + summary.py + context.py]** Puerto +
  memoria + Supabase (`category=books`) y resumen/contexto D48.
- [x] **Paso C4: [books/router.py + deps.py]** `POST /sources/goodreads/import`
  (texto CSV → normalizar → reemplazar → fresh; CSV inválido → 422),
  `GET /sources/books`, `GET /context/books`.
- [x] **Paso C5: [mcp_server.py + registry.py + main.py]** Tools `books.*` +
  resource; registrar y montar.
- [x] **Paso C6: [tests books]** Conector (fixture CSV), store, resumen,
  endpoints (import feliz/inválido/aislamiento), tools.
- [x] **Paso C7: [web]** `BooksDetail` con panel de import (file input →
  texto → POST, guía Goodreads, estados) + api ops + activación completa +
  test.

Bloque D — Import genérico y cierre:

- [x] **Paso D1: [imports/detection.py + imports/router.py]** Detección por
  firma de cabeceras (registry de firmas; v1 Goodreads) y `POST /imports`
  que delega; desconocido → 422 con guía; tests.
- [x] **Paso D2: [web/components/app/import-panel.tsx]** Panel de import
  genérico con guías por proveedor (v1: Goodreads; estructura para más),
  usado por `BooksDetail`.
- [x] **Paso D3: [mcp_server.py]** `profile.search` generalizado a los stores
  de items (games/film/anime/books) con hint actualizado + tests.
- [x] **Paso D4: [docs]** `current.md`, `roadmap.md` (Fase 3 → histórico),
  `decisions.md` (D45-D49), `por-revisar.md` (nuevos pendientes de infra:
  nada nuevo de keys — AniList sin key; verificación visual de las 3
  categorías), `data-model.md`/`architecture.md` si aplica.

### 4. Reporte de Pruebas

**[APROBADO]** — api: ruff y mypy sin incidencias (114 archivos); pytest
168/168 (41 nuevos: cliente AniList con MockTransport y errores GraphQL
embebidos, conector golden con dedupe, stores memoria + PostgREST simulado de
anime/books, resúmenes, servicio con perfil privado, endpoints con JWT de
anime/books/imports, import inválido sin tocar datos, límites de cuerpo por
ruta de import, tools MCP y `profile.search` cruzando categorías), cobertura
93.2%. web: tsc, eslint, vitest 55/55 (13 nuevos/actualizados: film/anime/
books-detail, panorama y fuentes con 5 categorías, enrutado del playground) y
build en verde (5 rutas de categoría prerenderizadas). Secretos: grep limpio
(solo nombres de campos, tokens de prueba en tests y textos de UI); AniList no
requiere key; el username viaja cifrado (Fernet) como D37/D41. Idioma D19
correcto. Sin migración (todo sobre `user_items`/`source_state`). Pendiente
del usuario: `TRAKT_CLIENT_ID` en Render y verificación e2e en producción
(por-revisar.md).
