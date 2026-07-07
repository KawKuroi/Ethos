# ACTIVE_TASK — Fase 4 · Borrado de cuenta con deshacer de 30 días (D53)

Zona de peligro de Ajustes real: borrar datos (conservando la cuenta) y borrar
la cuenta con purga diferida a 30 días, correo de aviso y deshacer.

### 1. Contexto y Archivos Afectados

Backend nuevo: `account/{__init__,models,service,mailer,auth_admin,deps,
router,purge_job}.py`, migración `0007_account_deletions.sql`,
`tests/account/test_account_api.py`. Editados: `auth.py` (`CurrentUserEmail`),
`main.py` (router). Web editado: `lib/api.ts` (ops de cuenta),
`settings/settings.tsx` (acciones reales + banner con deshacer) y su test.

### 2. Evaluación Crítica

Veredicto: **bueno**. El borrado diferido con marca en tabla + job de purga es
el patrón estándar; el deshacer es un simple delete de la marca. El borrado en
GoTrue (admin API) cascada por FK, así que la purga es un solo punto. Riesgos
controlados: las rutas exigen Supabase (503 sin él, nunca borran a medias); el
correo es best-effort y no bloquea. Deuda: el job de purga requiere que el
usuario lo programe (cron externo, por-revisar); el aviso depende del claim
`email` del JWT (si falta, no hay correo, pero el banner de Ajustes siempre
informa).

### 3. Plan de Acción Detallado

- [x] Migración 0007 + servicio (wipe, schedule, status, cancel, purge).
- [x] Router `/account/*` + deps (503 sin Supabase) + mailer + auth_admin.
- [x] Job `python -m ethos_api.account.purge_job` para el cron.
- [x] Web: ops en `lib/api.ts` + Ajustes real (banner fecha de purga, Deshacer).
- [x] Tests backend (9) y web (Settings reescrito, 4).
- [x] Docs: D53, roadmap, current, por-revisar.

### 4. Reporte de Pruebas

**[APROBADO]** — api: ruff + mypy limpios (146 archivos), pytest 201/201
(9 nuevos: wipe de tablas, programación con fecha, estado con/sin marca,
deshacer, 401, 503 sin Supabase, purga de vencidos, email del JWT), cobertura
91.3%. web: tsc + eslint limpios, vitest 70/70, build en verde. Secretos: grep
limpio (service_role solo por env). Idioma D19 correcto.
