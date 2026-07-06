# ACTIVE_TASK — Fase 4 · Sugerencias y contacto reales (D52)

Los formularios de sugerencias (landing y Ayuda) persisten de verdad y avisan
al admin por correo (opcional).

### 1. Contexto y Archivos Afectados

Backend nuevo: `feedback/{__init__,models,repository,mailer,deps,router}.py`,
migración `0006_feedback.sql`, `tests/feedback/test_feedback_api.py`. Editados:
`config.py` (SMTP + feedback_to/from), `main.py` (router). Web editado:
`lib/api.ts` (`submitFeedback`), `landing/suggestions.tsx`, `app/help/help.tsx`
y sus CSS + tests.

### 2. Evaluación Crítica

Veredicto: **bueno**. Mismo patrón repositorio (memoria+Supabase) y endpoint
público controlado (rate limit, `user_id` opcional, RLS sin acceso público).
El aviso por correo usa `smtplib` de la stdlib (sin dependencia nueva), es
opcional (gated por env) y best-effort en segundo plano: nunca bloquea ni
tumba el formulario. Deuda: el contacto personal sigue siendo el `mailto:` del
diseño (dirección real por configurar, por-revisar); no hay panel admin para
leer el feedback (se revisa en Supabase).

### 3. Plan de Acción Detallado

- [x] Migración 0006 + módulo `feedback/` (models, repo, mailer, router).
- [x] Config SMTP opcional; aviso best-effort en BackgroundTasks.
- [x] `submitFeedback` + cableado de landing y Ayuda (estados y errores).
- [x] Tests backend (8: persistencia, sesión, kind, validación, mailer) y web.
- [x] Docs: D52, roadmap, current, por-revisar.

### 4. Reporte de Pruebas

**[APROBADO]** — api: ruff + mypy limpios (136 archivos), pytest 192/192
(8 nuevos), cobertura 92.6%. web: tsc + eslint limpios, vitest 68/68, build en
verde. Secretos: grep limpio (SMTP solo por env; tokens de prueba en tests).
Idioma D19 correcto.
