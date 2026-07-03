# ACTIVE_TASK — Backend: slice Juegos/Steam (cierre programable de Fase 1)

Fase 1 · Backend. Completar el lado programable del slice: wishlist y
completado del conector, verificación OpenID de Steam, persistencia tras
puerto, generador de resumen, contexto descargable (D24), refresco con
estados de frescura, y el MCP con auth por token y tools `games.*` +
`profile.search` (D22/D28). El usuario delegó las decisiones abiertas.

### 1. Contexto y Archivos Afectados

El API ya tiene: contrato normalizado (`schema.py`), conector Steam
(biblioteca/recientes/perfil), credenciales cifradas con JWT de Supabase,
hardening y MCP montado con tool `ping`. Patrón establecido: puertos
(`Protocol`) con implementación en memoria primero (credenciales, D20) y
Supabase cuando se conecte la infra.

Afectados: `connectors/steam/{client,connector,openid}.py`, paquete nuevo
`games/` (store, summary, context, service, router), `mcp_auth.py`,
`mcp_server.py`, `main.py` y tests de cada pieza.

### 2. Evaluación Crítica — decisiones tomadas (delegadas por el usuario)

- **D32 · Wishlist**: `IWishlistService/GetWishlist/v1` (appid, priority,
  date_added). La respuesta no trae títulos y resolverlos exige una llamada
  de store por juego: en v1 la wishlist se persiste y expone como conteo +
  appids priorizados; los títulos se difieren (nota en el roadmap).
- **D33 · Completado agregado**: `GetPlayerAchievements` es una llamada por
  juego → presupuesto fijo: solo el top 20 por horas en cada refresco,
  protegido por el throttle existente del cliente. Sin logros o error →
  `None`; el agregado del resumen es la media de los calculados.
- **D34 · Forma del contexto** (concreta D24): `games.context.json` =
  `{namespace, provider, generated_at, profile, summary{games, hours,
  wishlisted, avg_completion_pct, last_synced_at}, top_by_hours[10],
  recently_played, wishlist{count, top_priority_appids}}`. Sin histórico de
  eventos en v1 (llega con Música/D17).
- **D35 · Persistencia**: puerto `GamesStore` (Protocol) + implementación en
  memoria indexada por usuario/appid, igual que credenciales. La migración
  Supabase (tabla `user_games` + RLS) queda explícitamente pendiente de
  infra; el roadmap lo refleja.
- **D36 · Refresco**: v1 con `BackgroundTasks` de FastAPI + estados de
  frescura en el store (`syncing/fresh/error` + `synced_at`; `stale` se
  deriva por edad >24 h). La cola durable (Supabase Queues) llega con la
  infra. Perfil privado (visibility != 3) → estado `private`.
- **OpenID (D12)**: el web maneja el redirect de Steam; la API verifica el
  retorno con `check_authentication` contra `steamcommunity.com` (validando
  los campos firmados) y guarda el steamid cifrado como credencial.
- **MCP (D22/D28)**: tokens `eth_live_…` emitidos con la sesión de Supabase
  (`POST /mcp-token`), guardados como hash SHA-256; las tools resuelven el
  usuario del header `Authorization` y sin token válido no sirven datos.
  Cada respuesta reporta KB servidos vs contexto total.

Deuda aceptada y anotada: stores en memoria (se pierden al redeploy; la web
sigue con datos de ejemplo hasta la migración Supabase), títulos de wishlist
diferidos, cola durable diferida.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [connectors/steam/client.py]** `get_wishlist` y
  `get_player_achievements` (throttled).
- [x] **Paso 2: [connectors/steam/connector.py]** wishlist → items
  `status=wishlist`; completado por appid → `extra.completion_pct`.
- [x] **Paso 3: [connectors/steam/openid.py]** verificación OpenID 2.0
  (`check_authentication`, campos firmados, extracción del steamid).
- [x] **Paso 4: [games/store.py]** `GamesStore` Protocol + memoria
  (items, perfil, estado de frescura por usuario).
- [x] **Paso 5: [games/summary.py]** resumen tipado desde items+perfil.
- [x] **Paso 6: [games/context.py]** `games.context.json` (D34).
- [x] **Paso 7: [games/service.py]** refresco: fetch → normalizar →
  completado top-20 → persistir; estados y perfil privado.
- [x] **Paso 8: [games/router.py + deps.py]** `POST /sources/steam`,
  `POST /sources/steam/refresh` (202), `GET /sources/games`,
  `GET /context/games`.
- [x] **Paso 9: [mcp_auth.py]** emisión/verificación de tokens `eth_live_…`
  (hash en memoria) + `POST /mcp-token`.
- [x] **Paso 10: [mcp_server.py]** resource `ethos://games/summary` y tools
  `games.summary`, `games.top_by_hours`, `games.recent`, `profile.search`
  con auth y métrica de KB (lógica separada y testeable).
- [x] **Paso 11: [main.py]** montar routers nuevos.
- [x] **Paso 12: [tests]** cliente (fixtures wishlist/achievements), openid
  (MockTransport), summary/context, service (fake connector), routers
  (JWT de prueba), tokens MCP y lógica de tools.

### 4. Reporte de Pruebas

**[APROBADO]** — ruff y mypy sin incidencias; pytest 77/77 (36 nuevos),
cobertura 95.5% (umbral 85%). Grep de secretos limpio (solo el prefijo
publico eth_live_ y nombres de variables). Idioma D19 correcto. Pendiente
unico de Fase 1: respaldo Supabase de los stores en memoria (D35).
