# ACTIVE_TASK — Backend: respaldo Supabase de la persistencia (D35)

Fase 1 · Backend. Sustituir los stores en memoria por el respaldo real en
Supabase: migración de tablas + RLS, repos PostgREST y selección automática
por entorno. Elegido por el usuario ("guiarme ahora con Supabase") tras el
cierre del slice.

### 1. Contexto y Archivos Afectados

Los puertos ya existían (`CredentialRepository`, `GamesStore`,
`McpTokenStore`); 0001 traía `source_state` y `profiles`, 0002
`user_credentials`. Afectados: `supabase/migrations/0003_*.sql`,
`supabase_rest.py` (nuevo), `credentials/{repository,deps}.py`,
`games/{store,deps}.py`, `mcp_auth.py` y tests.

### 2. Evaluación Crítica

- Tabla de items **genérica** (`user_items` con `category`), no `user_games`:
  Música (Fase 2) la reutiliza sin migración nueva. Payload jsonb =
  `NormalizedItem` completo + columnas extraídas para indexar.
- PostgREST con **service_role**: el backend ya autentica por JWT y acota por
  `user_id` (los refrescos en background no tienen JWT de usuario); RLS
  owner-only protege el acceso directo de cualquier otro cliente.
- `source_state` se amplía (estado `private`, `detail`, `provider_profile`)
  en vez de crear otra tabla de frescura: ya era su propósito (0001).
- `McpTokenStore` pasa a `Protocol` con memoria y Supabase, como el resto.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [supabase/migrations/0003_games_and_mcp_tokens.sql]**
  `user_items` + `mcp_tokens` + RLS + ampliación de `source_state`.
- [x] **Paso 2: [supabase_rest.py]** cliente PostgREST mínimo
  (select/insert/upsert/delete) + `get_rest()` según entorno.
- [x] **Paso 3: [credentials/repository.py]** `SupabaseCredentialRepository`.
- [x] **Paso 4: [games/store.py]** `SupabaseGamesStore` (items por payload,
  perfil y estado en `source_state`, mapeo fresh↔synced).
- [x] **Paso 5: [mcp_auth.py]** puerto + `SupabaseMcpTokenStore` (rotación por
  upsert de PK) + `InMemoryMcpTokenStore`.
- [x] **Paso 6: [deps]** selección automática memoria/Supabase en
  credenciales, juegos y tokens.
- [x] **Paso 7: [tests/test_supabase_repos.py]** MockTransport: upserts con
  on_conflict, delete con conteo, payload→modelo, mapeo de estados, hash del
  token (nunca el claro).

### 4. Reporte de Pruebas

**[APROBADO]** — ruff y mypy sin incidencias; pytest 84/84 (7 nuevos),
cobertura 94.6% (umbral 85%). Sin secretos (viaja solo el hash del token).
Queda en manos del usuario aplicar la migración 0003 (por-revisar.md); el
código selecciona Supabase solo cuando el entorno lo configura.
