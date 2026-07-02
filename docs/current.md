# Estado actual — Ethos

Estado vivo del proyecto. efesto lee este documento para saber en qué fase
estamos y lo actualiza al cerrar cada tarea (entrada con fecha `AAAA-MM-DD`).

## Estado general

Proyecto en arranque. El diseño de la interfaz (Claude Design) está terminado
y es la fuente de verdad de la UI (D25, `design.md`); los docs quedaron
re-planteados a partir de él el 2026-07-02. El trabajo de código sigue en
backend + infraestructura; `/web` se implementará contra el diseño.

## Activo

**Fase 1 — Slice Juegos / Steam** (en curso, backend). Hecho: contrato de datos
normalizado (`schema.py`) generalizado a `Category` con las 9 categorías (D27),
interfaz de conector (`connectors/base.py`), registro de conectores
(`connectors/registry.py`, D21) y conector de Steam (cliente HTTP +
normalización de biblioteca, jugados recientes y perfil) con tests de fixtures;
backend de credenciales de usuario (sesión por JWT de Supabase con JWKS,
cifrado Fernet y endpoints `/credentials`) sobre repositorio en memoria.
Pendiente de Fase 1: repositorio de credenciales respaldado por Supabase (con
estrategia RLS), persistencia indexada de juegos, wishlist y completado%
(decisiones abiertas), generador del resumen, tools del MCP de juegos, refresco
asíncrono, login OpenID y la web (Claude Design).

Pendiente de Fase 0 (requiere cuentas/credenciales): crear el proyecto Supabase
real y aplicar la migración, servicio en Render, proyecto en Vercel, keep-alive
ping y poblar el secret manager (llave de cifrado y Steam API key).

## Decisiones de inicialización

- Framework web: Next.js (App Router). Registrado como D18.
- Idioma del código: identificadores en inglés; texto humano en español.
  Registrado como D19 y detallado en `global.md`.
- Alcance del arranque: backend + infraestructura primero; `/web` después.

## Bitácora

### 2026-07-02 (Fase 1: contrato generalizado + registry)

- `MediaCategory` → `Category` con los 9 ids del diseño (games, music, film,
  anime, fitness, books, places, food, board) (D27) y registro de conectores
  `connectors/registry.py` (D21): (categoría, proveedor) → clase de conector,
  duplicado → ValueError, ausente → LookupError; Steam registrado. Credenciales
  y conector de Steam sobre el enum nuevo. Tests nuevos del registry y del
  catálogo. ruff, mypy y pytest (31, cobertura 96%) en verde.

### 2026-07-02 (revisión técnica)

- Revisión del backend con quick wins aplicados: verificación de JWT con
  soporte JWKS (ES256/RS256 con caché; HS256 legacy como fallback) y claims
  obligatorios (`exp`, `sub`, `aud`, `iss` si hay URL); `SecretStr` para los
  secretos de config; pin `fastmcp>=3.4,<4` y `httpx<1`; ruff con reglas `S`
  (bandit) y `RUF`; pytest-cov con umbral 85% (hoy ~95%); helpers de JWT
  deduplicados en `tests/helpers.py` + fixtures en `conftest.py`; tests
  nuevos (token expirado / sin exp / aud incorrecta / ES256 sin URL, roundtrip
  real del tool `ping` in-memory, DELETE 404, recently_played, respuesta
  no-dict de Steam); CI con cache de uv, push solo en main y `paths-ignore`
  de docs; corregida la mención "Fernet/AES-GCM" → Fernet (AES-128-CBC+HMAC).
  Roadmap: la generalización `Category` (9) se adelanta a Fase 1. Pendientes
  anotados para sus tareas: CORS al llegar `/web`, repositorio Supabase con
  Protocol async (API con JWT del usuario vía RLS; worker con service_role),
  validación de `provider` contra el registry (D21), Polars solo cuando llegue
  el primer import grande.

### 2026-07-02

- Diseño de Claude Design revisado (app, auth y landing) y adoptado como
  fuente de verdad de la UI. Docs re-planteados: nuevo `design.md` (tokens,
  pantallas, interacciones); PRD con las dos salidas del contexto (descarga +
  MCP) y el concepto "panel" (sustituye a "dump"); catálogo fijado en 9
  categorías con estados y despliegue secuencial —una por una, probada y
  confirmada antes de la siguiente; en la v1 solo Juegos activa y el resto
  "en desarrollo"; Pódcasts y YouTube del prototipo quedan fuera—; auth de la
  app = correo + Google + GitHub (Steam OpenID queda solo como conexión de
  fuente); tools del MCP con namespace (`games.top_by_hours`…) y métrica de
  KB servidos; web sin Recharts (tokens CSS + CSS Modules + SVG propio).
  Decisiones D24-D29; roadmap con la implementación del diseño en Fase 1 y
  pulido en Fase 4.

### 2026-06-30

- Backend de credenciales de usuario (D20): migración `0002_user_credentials.sql`
  (tabla + RLS owner-only), cifrado Fernet (`security.py`), verificación de JWT de
  Supabase (`auth.py`) y endpoints `/credentials` (conectar/listar/desconectar)
  sobre repositorio en memoria. Deps `cryptography` y `pyjwt`. ruff, mypy y
  pytest (17) en verde. Pendiente: repositorio respaldado por Supabase y su
  estrategia RLS. Confirmado: Steam sigue con OpenID + key del servidor (D12).

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
- Fase 1 (backend, parte 1): contrato normalizado (`schema.py`), interfaz de
  conector (`connectors/base.py`) y conector de Steam (`connectors/steam/`:
  cliente HTTP con httpx + normalización de biblioteca, jugados recientes y
  perfil). Tests de fixtures (golden-file) y `httpx.MockTransport`. `httpx`
  pasó a dependencia de runtime. ruff, mypy y pytest (8) en verde.
- Revisión de seguridad + planificación: auditado `/api` y `/supabase` (sin
  vulnerabilidad activa: sin secretos hardcodeados, RLS owner-only, timeouts, sin
  fuga de la API key). Planificado: sesión + credenciales cifradas
  (`user_credentials`, D20), registro de conectores (D21), guardrail de auth del
  MCP (D22) y catálogo de 9 categorías con generalización del contrato (D23).
  Docs actualizados (architecture, data-model, decisions, roadmap).
