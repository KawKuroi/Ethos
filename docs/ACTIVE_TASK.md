# ACTIVE_TASK — Fase 2: cablear la web para Música

Último ítem de Fase 2: sacar Música de "en desarrollo" y dejarla activa en la
web, consumiendo el backend ya construido (`/sources/listenbrainz`,
`/sources/music`, `/context/music`). Cierra el slice de Música de punta a punta.

### 1. Contexto y Archivos Afectados

El backend de música está completo (conector, event store, resumen por ventana,
refresco incremental, endpoints y tools MCP). La web tiene el slice de Juegos
como plantilla: `lib/api.ts` (Bearer + operaciones), hook `useGamesSource`,
`GamesDetail` (vista conectada/apagada/privada con datos reales), y las
pantallas Inicio (`overview`), Fuentes (`sources`) y Conectar IA (`connect`) que
hoy tratan Juegos como única fuente activa y el resto como "en desarrollo".
`CategoryDetail` es el detalle genérico (datos estáticos) que sirve a las
categorías aún en desarrollo.

Afectados: `lib/api.ts` (tipos + operaciones de música), `lib/use-source.ts`
(nuevo, hook genérico), `lib/use-games-source.ts` (envuelve el genérico),
`lib/use-music-source.ts` (nuevo), `components/app/category/data.ts` (Música
pasa de soon a live), `components/app/category/music-detail.tsx` (nuevo),
`components/app/connect-listenbrainz.tsx` (nuevo, alta por username),
`app/app/categoria/[slug]/page.tsx` (ruta music → MusicDetail),
`components/app/overview/{overview.tsx,data.ts}` (Música activa en el panorama),
`components/app/sources/sources.tsx` (tarjetas de Música),
`components/app/connect/data.ts` (consultas de música en el playground) y sus
tests.

### 2. Evaluación Crítica — decisiones tomadas

Veredicto: **bueno**. Es el cierre natural del slice; el backend ya expone todo
lo necesario y la web solo necesita una segunda fuente. Riesgo principal: la
tentación de un detalle "totalmente genérico" que fusione dos resúmenes muy
distintos (Juegos: horas/completado/deseados; Música: scrobbles/artistas/tracks)
en una sola forma, lo que sería una abstracción prematura que degrada ambas UIs.

Decisiones:

- **Slice de Música espejo del de Juegos (no fusión prematura)**: `MusicDetail`
  bespoke, fiel a la forma real del resumen musical (hero de escuchas, top
  artistas, top canciones), reutilizando el mismo `category.module.css` y el
  patrón de estados de `GamesDetail`. El `CategoryDetail` genérico se queda para
  las categorías aún en desarrollo (Cine, Anime, Libros).
- **Hook genérico `useSource<T>`**: se extrae la lógica común (loading/data/
  error/reload) a un hook parametrizado; `useGamesSource` pasa a envolverlo (sin
  cambiar su forma de retorno, para no tocar a sus consumidores) y `useMusicSource`
  lo reutiliza. Elimina duplicación sin churn en las pantallas existentes.
- **Alta de ListenBrainz por formulario de username (D37)**, no por redirección
  como Steam: `connect-listenbrainz.tsx` con un input y `POST /sources/listenbrainz`.
  Tras conectar, la vista muestra "sincronizando" con un botón para actualizar
  (el refresco corre en segundo plano en el backend).
- **Agregación de dos fuentes en Inicio y Fuentes**: el panorama y las tarjetas
  dejan de asumir a Juegos como única activa; se añade una fila/tarjeta de Música
  con su propia unidad (escuchas). La banda "El gusto en números" mantiene las
  cifras de Juegos (las más ricas) pero su meta cuenta las fuentes activas de
  forma dinámica; blindar un band mixto queda fuera de alcance (no está en el
  diseño) — se anota para verificación visual.

Deuda: la actividad reciente de Inicio sigue siendo solo de Juegos (el resumen
de música no expone una lista de listens recientes, solo tops); se revisará si
se añade un feed de eventos. El band de Inicio no mezcla métricas de música.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [lib/api.ts]** `SyncState` compartido (alias de `GamesSyncState`),
  tipos `MusicTopEntry`/`MusicSummary`/`MusicSource` y operaciones
  `getMusicSource`, `connectListenBrainz`, `refreshListenBrainz`,
  `downloadMusicContext`, `getMusicContextText`.
- [x] **Paso 2: [lib/use-source.ts]** hook genérico `useSource<T>(load)` →
  `{loading, data, error, reload}`.
- [x] **Paso 3: [lib/use-games-source.ts + lib/use-music-source.ts]**
  `useGamesSource` envuelve `useSource(getGamesSource)` manteniendo su forma;
  `useMusicSource` envuelve `useSource(getMusicSource)`.
- [x] **Paso 4: [components/app/connect-listenbrainz.tsx]** formulario de alta
  por username público (input + submit → `connectListenBrainz`, con estados).
- [x] **Paso 5: [components/app/category/music-detail.tsx]** detalle de Música:
  loading/error, conectar (formulario), sincronizando (con actualizar), y vista
  conectada (hero de escuchas, top artistas, top canciones, refrescar y modal de
  descarga reales contra `/context/music`).
- [x] **Paso 6: [components/app/category/data.ts]** `CATEGORY_DETAIL.music` pasa
  de `soon` a `live` (accent/name/provider/blurb/ns/slug).
- [x] **Paso 7: [app/app/categoria/[slug]/page.tsx]** ruta `music` → `MusicDetail`.
- [x] **Paso 8: [components/app/overview/{data.ts,overview.tsx}]** Música `live`
  en el panorama (fila propia con escuchas); meta de la banda cuenta las fuentes
  activas.
- [x] **Paso 9: [components/app/sources/sources.tsx]** tarjetas de Música
  (activa/apagada) y recuento de grupos con dos fuentes.
- [x] **Paso 10: [components/app/connect/data.ts]** consultas de música en el
  playground (`music.top_artists`), enrutado y textos actualizados.
- [x] **Paso 11: [tests]** `music-detail.test.tsx` nuevo; actualizar
  `category-detail`, `overview`, `sources` y `connect` para la presencia de
  Música.

### 4. Reporte de Pruebas

**[APROBADO]** — tsc, eslint y build sin incidencias; vitest 42/42 (4 nuevos:
3 de `MusicDetail` + 1 de enrutado de música en el playground). Build genera
`/app/categoria/music` prerenderizada. Secretos: ListenBrainz se lee por
username público, sin tokens; grep limpio. Idioma D19 correcto. Con esto Música
queda activa de punta a punta en la web (detalle propio, alta por username,
panorama e Inicio, Fuentes y consultas de música en Conectar IA). Pendiente del
usuario: aplicar la migración 0004 y verificar el flujo real (por-revisar.md).
