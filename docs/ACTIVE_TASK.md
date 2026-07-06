# ACTIVE_TASK — Fase 4 · Aviso de categorías en desarrollo (D50)

Primera tarea de la Fase 4: las categorías diferidas (Lugares, Comida, Juegos
de mesa) se muestran "en desarrollo" con un "Avísame cuando esté lista" que
persiste el correo.

### 1. Contexto y Archivos Afectados

Backend nuevo: `interest/{__init__,models,repository,deps,router}.py`,
migración `0005_category_interest.sql`. Editados: `auth.py`
(`get_optional_user_id`), `main.py` (router), `pyproject.toml`
(`email-validator`). Web nuevo: `components/notify-form.{tsx,module.css}`.
Editados: `lib/api.ts` (`registerCategoryInterest`), `landing/data.ts` +
`gallery.tsx` + `landing.module.css` (bloque "En camino"), `category/data.ts`
(entradas soon), `category/category-detail.tsx` + `.module.css` (pantalla soon
con aviso), `lib/use-active-sources.ts` + `overview.tsx` (filas soon),
`sources.tsx` (excluye soon de apagadas). Tests actualizados: landing, sources,
category-detail; nuevos: `interest/test_interest_api.py`, `notify-form.test.tsx`.

### 2. Evaluación Crítica

Veredicto: **bueno**. Reutiliza el patrón repositorio (memoria+Supabase) y el
estado "soon" ya existente del diseño. Endpoint público controlado (rate limit
por IP, idempotente por correo+categoría, valida el set diferido, RLS sin
políticas públicas). Riesgo menor: endpoint sin auth = superficie de spam,
mitigado por el rate limit y el upsert idempotente. Deuda: el aviso real al
lanzar una categoría queda pendiente (necesita proveedor de correo, ver tarea
de sugerencias/contacto).

### 3. Plan de Acción Detallado

- [x] Migración 0005 + slice `interest/` (modelos, repo, deps, router público).
- [x] `get_optional_user_id` en `auth.py`; `email-validator` en pyproject.
- [x] `registerCategoryInterest` + `NotifyForm` compartido.
- [x] Resurfacar diferidas: landing "En camino", panorama, Fuentes, pantalla soon.
- [x] Tests backend (6) y web (NotifyForm + ajustes a landing/sources/detail).
- [x] Docs: D50, roadmap, current, por-revisar.

### 4. Reporte de Pruebas

**[APROBADO]** — api: ruff + mypy limpios (121 archivos), pytest 174/174
(6 nuevos), cobertura 93.0%. web: tsc + eslint limpios, vitest 64/64, build en
verde (8 rutas de categoría: 5 activas + 3 soon). Secretos: grep limpio (solo
nombres de campos y correos de ejemplo en tests). Sin credenciales nuevas
(AniList/interés no requieren keys). Idioma D19 correcto.
