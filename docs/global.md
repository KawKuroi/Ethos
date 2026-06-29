# Reglas globales — Ethos

Documento que fija las convenciones invariables del proyecto. Lo lee el
orquestador efesto en cada tarea (junto con `prd.md` y `architecture.md`) y
manda sobre cualquier criterio por defecto.

## 1. Idioma

- **Código (identificadores)**: inglés. Variables, funciones, clases, módulos,
  tablas y columnas de base de datos, claves de JSON/API y nombres de archivo de
  código van en inglés (`total_hours`, `last_session`, `playtime_pct`,
  `user_games`, `getOwnedGames`). Sin acentos ni eñes en identificadores.
- **Texto humano**: español. Comentarios, docstrings, documentación (`/docs`),
  mensajes de commit, textos de la interfaz, mensajes de error visibles y
  literales de log van en español, con acentos correctos.
- Excepción: los tokens de Conventional Commits (`feat`, `fix`, `refactor`,
  `BREAKING CHANGE`, etc.) van en inglés por estándar.

Los nombres en español que aparecen en los docs de modelo de datos son
descriptivos (prosa), no DDL literal: al implementar se traducen a inglés.

## 2. Stack y herramientas

| Capa | Tecnología | Gestor |
|------|-----------|--------|
| Web (`/web`) | TypeScript — Next.js (App Router) + Recharts | pnpm |
| Backend + MCP (`/api`) | Python — FastAPI + FastMCP (un servicio) | uv |
| Procesamiento | Polars + Pydantic v2 | uv |
| Datos / auth / secretos / cola | Supabase (Postgres + Auth + Vault + Queues) | — |
| Repositorio | Monorepo | — |

Hospedaje: web en Vercel, backend+MCP en Render, datos en Supabase. Objetivo de
costo: 0 USD/mes (free tiers).

## 3. Estructura del repositorio

```
/                 raíz del monorepo
  /api            backend Python: FastAPI + FastMCP, conectores, normalización
  /web            app Next.js (la diseña Claude Design; se integra después)
  /packages       tipos y contratos compartidos (TS generados desde el esquema)
  /supabase       migraciones SQL, esquema y políticas RLS
  /docs           documentación de contexto (este directorio)
  /.github        CI (GitHub Actions)
```

## 4. Estándares de calidad

- **Tests en todas las capas** (decisión D15): conectores (golden-file),
  normalización, API, tools del MCP (en memoria), web (componentes + E2E).
- Verificación por stack antes de cada commit:
  - Python (`/api`): `ruff` (lint), `mypy` (tipos), `pytest` (tests).
  - TypeScript (`/web`, `/packages`): `tsc --noEmit`, `eslint`, build, tests.
- Sin tipos inseguros nuevos (`Any` en Python sin justificar, `any` en TS).
- Un warning de linter, error de tipos/compilación o fallo de suite = bloqueo.

## 5. Seguridad

- **Cero secretos en el repo**. Credenciales y llaves solo en variables de
  entorno / secret manager. `*.env` fuera de git; se versiona `.env.example`.
- Tokens de terceros cifrados a nivel de app antes de persistir (D9).
- El token con que la IA se autentica ante el MCP nunca se reenvía a APIs de
  terceros (las tools usan las credenciales del servidor).
- Aislamiento por usuario con Row-Level Security en Postgres.

## 6. Convenciones de commits

Conventional Commits 1.0.0. Type en inglés
(`feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`), scope en
español opcional, subject en español (<=50 chars, imperativo, tercera persona,
sin punto final ni emoji). Body opcional explicando el porqué (líneas <=72).
`BREAKING CHANGE:` solo si aplica. Sin `Co-Authored-By` salvo petición.

## 7. Documentos de contexto (`/docs`) y efesto

efesto reconoce cinco docs base más documentos de apoyo:

- `prd.md` — qué se construye y para quién.
- `architecture.md` — stack, hospedaje, flujo de datos y seguridad.
- `roadmap.md` — fases con checkboxes y `## Histórico de fases completadas`.
- `current.md` — estado vivo: fase activa, estado general y bitácora con fechas.
- `global.md` — este documento (reglas invariables).
- Apoyo: `data-model.md`, `decisions.md`.

Reglas operativas de efesto: cero invenciones (ante ambigüedad real, preguntar),
cero emojis, output condensado, dos únicos gates (enfoque y commit). El `commit`
final cubre `git add` + `commit` + `push`.
