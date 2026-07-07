# ACTIVE_TASK — Fase 4 · Cobertura y empaquetado (D59, cierre de fase)

Última tarea de la Fase 4: objetivos de cobertura con gates en CI y cierre del
empaquetado (versión 0.2.0).

### 1. Contexto y Archivos Afectados

Editados: `api/pyproject.toml` (versión 0.2.0, `--cov-fail-under=88`),
`api/src/ethos_api/{__init__,main}.py` (versión), `web/package.json` (0.2.0,
`test` con cobertura, `@vitest/coverage-v8`), `web/vitest.config.ts`
(thresholds), `README.md` (línea del contenedor), `docs/` (roadmap con la fase
al histórico, current, decisions).

### 2. Evaluación Crítica

Veredicto: **bueno**. Los gates se fijan ~3 puntos bajo la medición real:
bloquean regresiones sin volverse ruido, y se suben conforme crezca la
cobertura. `pnpm test` con cobertura integra el gate en el CI existente sin
tocar el workflow. "Empaquetado" de un monorepo hospedado = sus despliegues
(Render blueprint completo, Dockerfile D58, Vercel); no hay artefactos
instalables que publicar. Deuda: la cobertura web (57%) tiene margen — los
gates documentan el punto de partida, no la meta.

### 3. Plan de Acción Detallado

- [x] api: gate 85→88; versión 0.2.0 (pyproject, __init__, FastAPI).
- [x] web: `@vitest/coverage-v8`, thresholds por dimensión medidos, `test` con
  cobertura, versión 0.2.0.
- [x] README: línea del contenedor.
- [x] Docs: D59, Fase 4 al histórico del roadmap, pendientes nuevos, current.

### 4. Reporte de Pruebas

**[APROBADO]** — api: pytest 213/213, cobertura 90,3% con gate 88. web: vitest
75/75 con gates de cobertura pasando (57,0/63,5/55,4/59,7 vs 53/60/52/56), tsc,
eslint y build en verde. Secretos: grep limpio. Idioma D19 correcto.
