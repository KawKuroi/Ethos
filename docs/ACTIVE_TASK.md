# ACTIVE_TASK — Web: Fuentes

Fase 1 · Web. Vista única de Fuentes del diseño (`App Ethos.dc.html`): resumen
(4 cifras) y grupos Activas / Apagadas / En desarrollo, cada categoría con su
salud/estado y acceso al detalle. v1: Juegos activa; Música/Cine/Anime/Libros en
desarrollo; sin apagadas (grupo oculto).

### 1. Contexto y Archivos Afectados

Reutiliza `CATEGORY_DETAIL` (nombre, proveedor, accent, salud, fresh, modo,
soonEta). Cards enlazan al detalle (`/app/categoria/<slug>`).

Archivos (se crean salvo indicación):
- `web/src/components/app/sources/*` — componente, estilos y test.
- `web/src/app/app/fuentes/page.tsx` (mod) — renderiza `<Sources/>`.

### 2. Evaluación Crítica

**Veredicto: directa; deriva de los datos de categoría.** Opción recomendada:
resumen + Activas + En desarrollo (Apagadas oculto en v1). Deuda: método
API/import no se muestra aún (no aporta sin apagadas); datos de ejemplo.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [sources/sources.module.css]** estilos: grid de resumen (4),
  encabezados de grupo, cards activa/soon con salud y CTA.
- [x] **Paso 2: [sources/sources.tsx]** deriva de `CATEGORY_DETAIL`: resumen
  (activas · expuestas por MCP · apagadas · en desarrollo), grupo Activas (card
  con inicial, salud, proveedor·modo·fresh, "Abrir →" al detalle) y grupo En
  desarrollo (card con icono, proveedor·ETA, chip "Próximamente"); Apagadas solo
  si las hubiera. `eth-screen`.
- [x] **Paso 3: [app/app/fuentes/page.tsx]** renderiza `<Sources/>`.
- [x] **Paso 4: [sources/sources.test.tsx]** resumen visible, Juegos en Activas
  con enlace al detalle, y las cuatro categorías en desarrollo.

### 4. Reporte de Pruebas

**[APROBADO]** — tsc, eslint sin incidencias; vitest 28/28 (3 nuevos de
`sources`); build OK. Idioma correcto; secretos limpio; sin `any` nuevos.
Verificación visual real: la hace el usuario en producción.
