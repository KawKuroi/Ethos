# Estado actual — Ethos

Estado vivo del proyecto. efesto lee este documento para saber en qué fase
estamos y lo actualiza al cerrar cada tarea (entrada con fecha `AAAA-MM-DD`).

## Estado general

Proyecto en arranque. Documentación de contexto completa y adaptada a efesto.
La interfaz (`/web`) se está diseñando aparte con Claude Design. El trabajo de
código inicial se centra en backend + infraestructura.

## Activo

**Fase 0 — Fundación** (en curso). Andamiado: backend `/api` (FastAPI + FastMCP
en un solo servicio, `/health` + `/mcp`), esquema base en `/supabase` con RLS,
CI en GitHub Actions, `.gitignore` y `.env.example`. `/web` se deja para Claude
Design e integración posterior.

Pendiente de Fase 0 (requiere cuentas/credenciales): crear el proyecto Supabase
real y aplicar la migración, servicio en Render, proyecto en Vercel, keep-alive
ping y poblar el secret manager (llave de cifrado y Steam API key).

## Decisiones de inicialización

- Framework web: Next.js (App Router). Registrado como D18.
- Idioma del código: identificadores en inglés; texto humano en español.
  Registrado como D19 y detallado en `global.md`.
- Alcance del arranque: backend + infraestructura primero; `/web` después.

## Bitácora

### 2026-06-29

- Documentación de contexto adaptada a efesto: añadidos `global.md` (reglas
  invariables, convención de idioma) y `current.md` (este archivo); `roadmap.md`
  convertido a checkboxes con sección de histórico; decisiones D18-D19 añadidas.
- Repositorio remoto creado en GitHub (`KawKuroi/Ethos`). Git local pendiente de
  inicializar y conectar.
- Andamiaje de Fase 0 (backend + infra): creado `/api` (FastAPI + FastMCP, un
  solo servicio con `/health` y `/mcp`, tool `ping`, tests), `/supabase`
  (migración `0001_foundation.sql` con `profiles`, `source_state`, índices,
  triggers y RLS owner-only), CI (`.github/workflows/ci.yml`), `.gitignore` y
  `.env.example`. Verificado en local: ruff, mypy y pytest en verde. Eliminado
  `design-brief.md` (no lo usa efesto). README del proyecto actualizado.
