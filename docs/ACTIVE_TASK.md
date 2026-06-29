# ACTIVE_TASK — Fase 0: andamiaje backend + infraestructura

Tarea: crear el esqueleto de código e infraestructura del monorepo, sin diseño
ni `/web` (lo lleva Claude Design). Cubre los bullets de Fase 0 que no requieren
cuentas externas: monorepo + `/api` (FastAPI+FastMCP), esquema base en
`/supabase` con RLS, CI en GitHub Actions, configuración raíz, y git local.

## 1. Contexto y Archivos Afectados

Proyecto greenfield: no hay código previo, se crean archivos nuevos (el límite
de 5 archivos del Lector aplica a lectura de código existente, no a un
andamiaje). Archivos a crear:

- `.gitignore` — Python, Node, env, OS, IDE.
- `.env.example` — variables de entorno sin valores (sin secretos).
- `api/pyproject.toml` — proyecto Python (uv), deps mínimas y dev.
- `api/.python-version` — fija intérprete compatible.
- `api/README.md` — cómo correr el backend.
- `api/src/ethos_api/__init__.py`
- `api/src/ethos_api/config.py` — Settings con pydantic-settings (env only).
- `api/src/ethos_api/main.py` — FastAPI, `/health`, monta el MCP.
- `api/src/ethos_api/mcp_server.py` — FastMCP (stateless), tool `ping` de prueba.
- `api/tests/__init__.py`
- `api/tests/test_health.py` — verifica `/health`.
- `api/tests/test_mcp.py` — verifica que el MCP está montado.
- `supabase/migrations/0001_foundation.sql` — `profiles`, `source_state`, RLS.
- `supabase/README.md` — cómo aplicar migraciones.
- `.github/workflows/ci.yml` — lint + tipos + tests de `/api`.

Fuera de esta tarea (requieren cuentas/credenciales, quedan abiertos en
roadmap): proyecto Supabase real, servicio Render, proyecto Vercel, keep-alive,
valores del secret manager. Diferidos a Fase 1: polars, cliente Supabase y las
tablas específicas de Steam (`games`, `user_games`, `user_wishlist`,
`user_profile_steam`).

## 2. Evaluación Crítica

**Veredicto: viable / bueno.** El enfoque (andamiar backend+infra y dejar `/web`
a Claude Design) es de bajo riesgo y respeta la arquitectura: el documento pide
"un único servicio combinando API y endpoint `/mcp`", y `main.py` montando
FastMCP bajo `/mcp` lo cumple. No hay choque con PRD/arquitectura.

Decisiones con trade-off (recomendada marcada):

1. **Versión de Python**: el sistema tiene 3.14.5, muy nuevo; varios paquetes
   (FastMCP y, más adelante, polars/pydantic-core) pueden no tener wheels aún.
   - (Rec.) Fijar Python 3.12 vía `uv` → wheels estables, sin compilar.
   - Usar 3.14 del sistema → riesgo de fallos de instalación.

2. **Dependencias ahora**: minimalismo vs completo.
   - (Rec.) Mínimas: fastapi, uvicorn, fastmcp, pydantic-settings + dev
     (pytest, ruff, mypy, httpx). Fase 0 solo pide "tests vacíos corriendo".
   - Completo (incluir polars, supabase) → instala más, sin uso real aún.

3. **Alcance del SQL**: fundación vs esquema Steam completo.
   - (Rec.) Solo fundación: `profiles` (ligada a `auth.users`) y `source_state`,
     ambas con RLS. Las tablas de Steam son de Fase 1.
   - Esquema Steam completo ahora → adelanta decisiones de tipos de Fase 1.

**Deuda técnica prevista (concreta):**
- *MCP ↔ FastAPI*: el `lifespan` del app de FastMCP debe pasarse a FastAPI o la
  inicialización de sesión MCP falla. Mitigación: test de montaje + verificación.
- *Despliegue*: sin configs de Render/Vercel todavía; esos bullets quedan
  abiertos y dependen de cuentas. Riesgo: olvidarlos; mitigado en `current.md`.
- *Tooling*: `pnpm` y `gh` no instalados; se necesitarán para `/web` y PRs.
- *RLS*: las políticas deben validarse contra Supabase Auth (`auth.uid()`); sin
  proyecto real solo se valida sintaxis, no comportamiento. Riesgo aceptado.
- *Push*: el remoto ya puede tener un commit inicial; el primer push podría
  divergir. Se reportará sin forzar (regla del Publicador).

## 3. Plan de Acción Detallado

### Bloque A — Configuración raíz
- [x] **Paso 1: [.gitignore]** ignorar `.venv/`, `__pycache__/`, `*.pyc`,
  `.env`, `.env.*` (salvo `.env.example`), `node_modules/`, `.next/`, `dist/`,
  `.DS_Store`, `.idea/`, `.vscode/` (salvo settings compartibles), `.mypy_cache/`,
  `.pytest_cache/`, `.ruff_cache/`.
- [x] **Paso 2: [.env.example]** claves sin valores con comentario en español:
  `ENVIRONMENT`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`,
  `ENCRYPTION_KEY`, `STEAM_API_KEY`. Ningún valor real.

### Bloque B — Backend `/api`
- [x] **Paso 3: [api/pyproject.toml]** metadata, `requires-python = ">=3.12"`,
  deps mínimas y grupo dev; configurar ruff, mypy y pytest; build con hatchling
  (paquete `ethos_api` en `src/`).
- [x] **Paso 4: [api/.python-version]** fijar `3.12`.
- [x] **Paso 5: [api/src/ethos_api/__init__.py]** versión del paquete.
- [x] **Paso 6: [api/src/ethos_api/config.py]** `Settings(BaseSettings)` leyendo
  del entorno (sin valores por defecto sensibles), con `environment`.
- [x] **Paso 7: [api/src/ethos_api/mcp_server.py]** instancia `FastMCP`
  (stateless), una tool `ping` de prueba; expone el app ASGI del MCP.
- [x] **Paso 8: [api/src/ethos_api/main.py]** crea FastAPI con el `lifespan` del
  MCP, endpoint `GET /health`, y monta el MCP en `/mcp`.
- [x] **Paso 9: [api/README.md]** instrucciones con `uv` (sync, run, test).

### Bloque C — Tests `/api`
- [x] **Paso 10: [api/tests/__init__.py]** paquete de tests.
- [x] **Paso 11: [api/tests/test_health.py]** `TestClient` → `/health` devuelve
  200 y estado ok.
- [x] **Paso 12: [api/tests/test_mcp.py]** verifica que la ruta `/mcp` está
  montada (no 404).

### Bloque D — Datos `/supabase`
- [x] **Paso 13: [supabase/migrations/0001_foundation.sql]** extensiones,
  tabla `profiles` (id → `auth.users`, timestamps) y `source_state`
  (user_id, category, provider, mode, last_synced_at, status), índices,
  `ENABLE ROW LEVEL SECURITY` y políticas owner-only (`auth.uid()`); comentarios
  en español, identificadores en inglés.
- [x] **Paso 14: [supabase/README.md]** cómo aplicar la migración (Supabase CLI).

### Bloque E — CI
- [x] **Paso 15: [.github/workflows/ci.yml]** en push/PR: instalar uv, `uv sync`,
  `ruff check`, `mypy`, `pytest` sobre `/api`. (Job de `/web` se añadirá al
  integrarla.)

### Bloque F — Git local (en el Publicador)
- [ ] **Paso 16:** `git init`, conectar remoto `KawKuroi/Ethos`, stagear lo
  creado + `/docs`, commit, push (todo tras el gate de commit).

## 4. Reporte de Pruebas

**[APROBADO]**

- Cumplimiento funcional: backend con `/health` y MCP montado en `/mcp`, según
  el plan y la arquitectura (un solo servicio API+MCP).
- Idioma del código: identificadores en inglés, comentarios/docstrings en
  español (conforme a `global.md`).
- Secretos: grep sin coincidencias en lo modificado; `.env` ignorado, solo
  `.env.example` (vacío) versionado.
- Verificación de stack (`/api`, uv): `ruff check` sin issues; `mypy` sin
  issues (7 archivos); `pytest` 2 passed.
- Incidencia resuelta: la versión instalada de FastMCP movió `stateless_http`
  del constructor a `http_app()`; corregido el wiring y reverificado en verde.
