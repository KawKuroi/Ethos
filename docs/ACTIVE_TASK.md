# ACTIVE_TASK — Fase 4 · OAuth 2.1 en el MCP (D56)

Migración del auth del MCP al patrón OAuth 2.1 del spec MCP, manteniendo el
token legacy `eth_live_` (D22).

### 1. Contexto y Archivos Afectados

Backend nuevo: `oauth/{__init__,models,store,deps,router}.py`, migración
`0008_oauth_mcp.sql`, `tests/oauth/test_oauth_flow.py`. Editados: `config.py`
(`public_base_url`, `web_base_url`), `mcp_auth.py` (`resolve_bearer_user`),
`mcp_server.py` (`_require_user` por el punto único), `middleware.py`
(`McpAuthChallengeMiddleware`), `main.py` (router + middleware),
`tests/conftest.py` (reset del rate limit entre tests). Web nuevo:
`app/oauth/autorizar/page.tsx`, `components/oauth/consent.{tsx,module.css}` +
test; `lib/api.ts` (`approveOAuth`).

### 2. Evaluación Crítica

Veredicto: **bueno**, con alcance deliberadamente mínimo: AS integrado (una
sola pieza que mantener), clientes públicos con PKCE S256 obligatorio y
redirect exact-match (https o loopback), tokens como hash con expiración y
refresh rotatorio, y 401 con `resource_metadata` para el autodescubrimiento.
Riesgos controlados: los codes en memoria se pierden en redeploy (el cliente
reintenta; documentado); `/mcp` deja de responder anónimo (endurece D22, ojo
monitores). Deuda: sin UI de revocación por cliente (revocar = borrar filas de
`oauth_tokens`; la lista de clientes autorizados en Ajustes queda como mejora);
`scope` es informativo (una sola categoría de permiso, lectura).

### 3. Plan de Acción Detallado

- [x] Migración 0008 (`oauth_clients`, `oauth_tokens`) + stores memoria/Supabase.
- [x] Router: discovery (8414/9728), register (7591), authorize → consentimiento
  web, approve (JWT), token (code+PKCE / refresh rotatorio, form a mano).
- [x] `resolve_bearer_user` (legacy + OAuth) y desafío 401 en `/mcp`.
- [x] Web: `/oauth/autorizar` (sesión Supabase, autorizar/denegar) + `approveOAuth`.
- [x] Tests: flujo completo, PKCE malo, code de un solo uso, refresh rotatorio,
  denegar, redirect no registrada, registro inseguro, discovery, 401 y paso con
  token OAuth (10) + consent web (4). Fix del rate limit de la suite.
- [x] Docs: D56, roadmap, current, por-revisar.

### 4. Reporte de Pruebas

**[APROBADO]** — api: ruff + mypy limpios (153 archivos), pytest 213/213,
cobertura 90.3%. web: tsc + eslint limpios, vitest 75/75, build en verde con
`/oauth/autorizar` prerenderizada. Secretos: grep limpio (prefijos públicos de
token señalados; solo hashes persisten). Idioma D19 correcto.
