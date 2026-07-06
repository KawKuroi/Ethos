# ACTIVE_TASK — Fase 4 · Entradas a mano (D51)

Registros añadidos a mano (sin proveedor) en las categorías de obra.

### 1. Contexto y Archivos Afectados

Backend nuevo: `items/{__init__,support,models,service,router}.py`,
`tests/items/test_items_api.py`. Editados: los cuatro stores de item
(`games/film/anime/books/store.py`) con `add_item`/`delete_item` y refresco que
conserva las entradas a mano; `main.py` (router). Web nuevo:
`category/manual-entries.{tsx,module.css}` + test. Editados: `lib/api.ts`
(ops de items), los cuatro detalles (`games/film/anime/books-detail.tsx`) con
el bloque `ManualEntries`, y sus tests (mock de `@/lib/api`).

### 2. Evaluación Crítica

Veredicto: **bueno**. Reutiliza `user_items` sin migración; al vivir junto a
los del proveedor, resúmenes/contexto/MCP los incluyen sin tocar esos caminos.
El punto delicado —que el refresco no borre lo manual— se resuelve acotando el
borrado (`external_id not like 'manual:*'` / `keep_manual`), cubierto por test.
Deuda: la UI de entradas a mano solo está en el detalle conectado (extender a
categorías sin proveedor queda como mejora, por-revisar). Música queda fuera
(es de eventos).

### 3. Plan de Acción Detallado

- [x] Módulo `items/` (support, models, service, router genérico por categoría).
- [x] `add_item`/`delete_item` + refresco seguro en los 4 stores (memoria+Supabase).
- [x] `lib/api.ts` (list/add/delete) + `ManualEntries` en los 4 detalles.
- [x] Tests backend (10) y web (`ManualEntries`) + mocks de detalles.
- [x] Docs: D51, roadmap, current, por-revisar.

### 4. Reporte de Pruebas

**[APROBADO]** — api: ruff + mypy limpios (126 archivos), pytest 184/184
(10 nuevos: alta/lista/borrado, resumen que cuenta lo manual, refresco que lo
conserva, aislamiento, categoría sin soporte, id no manual, inexistente),
cobertura 92.6%. web: tsc + eslint limpios, vitest 67/67 (ManualEntries +
mocks de los 4 detalles), build en verde. Secretos: grep limpio. Sin migración.
Idioma D19 correcto.
