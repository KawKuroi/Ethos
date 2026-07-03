# ACTIVE_TASK — Web: Detalle de categoría (Juegos)

Fase 1 · Web. Pantalla de Detalle de categoría del diseño (`App Ethos.dc.html`):
para Juegos (conectada) — back, header con Refrescar y Descargar contexto,
status strip (salud · proveedor · modo API/Import · actualizado), stat band
(hero + sparkline + 4 stats), Destacados / Reciente / Listas, y modal "Descargar
contexto" con preview JSON/MCP + copiar/descargar. Para las categorías en
desarrollo (Música/Cine/Anime/Libros) — el estado "en desarrollo".

### 1. Contexto y Archivos Afectados

Ruta `/app/categoria/[slug]` (slug = games/music/film/anime/books). El panorama
de Inicio enlaza aquí. Datos de ejemplo del prototipo (constantes). El estado
"apagada" (guía de import) no aplica en v1 (ninguna categoría está apagada) → se
difiere. Cambiar proveedor y modo se muestran, sin diálogo (se difiere). Eliminar
datos vive en Ajustes → no se duplica aquí.

Archivos (se crean salvo indicación):
- `web/src/components/app/category/*` — datos, estilos, detalle (client) y test.
- `web/src/app/app/categoria/[slug]/page.tsx` — resuelve slug → detalle o 404.
- `web/src/components/app/nav.ts` (mod) — `metaForPath` para la ruta de categoría.
- `web/src/components/app/overview/overview.tsx` (mod) — filas del panorama
  enlazan a `/app/categoria/<id>`.

### 2. Evaluación Crítica

**Veredicto: buena, la pantalla más rica; encaja con Inicio.** Opciones: (1)
conectada (Juegos) + en desarrollo + modal de descarga **[recomendada]**; (2)
+ estado apagado con guía import — innecesario en v1; (3) + diálogo de cambio de
proveedor — se difiere. Deuda: datos de ejemplo (backend luego); refresco y
copiar/descargar como efímeros de UI; navegación de vuelta a Inicio.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [category/data.ts]** `CATEGORY_DETAIL` por slug: Juegos completo
  (provider, ns, blurb, hero, spark, stats, top, recent, tags, salud, fresh,
  ctxKb) y Música/Cine/Anime/Libros como `soon` (nota + ETA).
- [x] **Paso 2: [category/sparkline.ts]** helper que mapea la serie a puntos del
  polyline (100×26), como `spark()` del prototipo.
- [x] **Paso 3: [category/context.ts]** genera el preview JSON y MCP del contexto
  desde los datos de la categoría (como `ctxJson`/`ctxMcp`).
- [x] **Paso 4: [category/category.module.css]** estilos: header, status strip,
  stat band (hero+sparkline+grid), secciones top/recent/tags, estado soon, modal.
- [x] **Paso 5: [category/category-detail.tsx]** ("use client") arma la pantalla:
  conectada (Juegos) con Refrescar (efímero), Descargar contexto (abre modal),
  status strip, stat band, Destacados/Reciente/Listas; y estado soon. Modal con
  pestañas JSON/MCP, copiar ("Copiado ✓") y descargar (`<slug>.context.json`).
- [x] **Paso 6: [app/app/categoria/[slug]/page.tsx]** resuelve el slug (404 si no
  existe) y renderiza `<CategoryDetail/>`.
- [x] **Paso 7: [nav.ts]** `metaForPath` devuelve el nombre de la categoría +
  "Fuente de contexto para tu IA" para `/app/categoria/<slug>`.
- [x] **Paso 8: [overview/overview.tsx]** las filas del panorama enlazan al
  detalle (`/app/categoria/<id>`).
- [x] **Paso 9: [category/category-detail.test.tsx]** Juegos muestra stats/top;
  el modal abre y alterna JSON/MCP; una categoría soon muestra "en desarrollo".

### 4. Reporte de Pruebas

**[APROBADO]**

- tsc, eslint sin incidencias; `vitest run` 25/25 (3 nuevos de `category-detail`).
- `next build`: OK; `/app/categoria/[slug]` prerenderiza games/music/film/anime/
  books. Idioma correcto; secretos limpio; sin `any` nuevos.
- Verificación visual real: la hace el usuario en producción.
