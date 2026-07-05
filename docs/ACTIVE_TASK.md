# ACTIVE_TASK — Fase 2: Música / ListenBrainz (backend)

Fase 2, chunk backend. Segunda categoría sobre los puertos de Fase 1, pero
estrenando el **modelo de eventos con timestamp** y la consulta temporal real
("más escuchadas en los últimos 30 días"). Decisiones delegadas por el usuario.

### 1. Contexto y Archivos Afectados

Fase 1 dejó: contrato `NormalizedItem` (obra + relación), registro de conectores
(D21), stores tras puerto (memoria + Supabase), MCP con auth por token y el
slice de Juegos como plantilla. Música es de tipo evento (listens con
timestamp), no "obra + relación": necesita un contrato y un store propios.

Afectados: `schema.py` (contrato de evento), `connectors/base.py` (generalizar
la salida), `connectors/listenbrainz/*` (nuevo), `music/*` (nuevo: store,
summary, service, router, deps), `mcp_server.py` (tools `music.*`),
`connectors/registry.py`, `main.py`, `supabase/migrations/0004_*.sql` y tests.

### 2. Evaluación Crítica — decisiones tomadas

- **D37 · Conexión de Música**: ListenBrainz se lee por **username público** (su
  API de listens no requiere OAuth). El username se guarda como credencial del
  proveedor `listenbrainz` (categoría music), cifrado como el steamid.
- **D38 · Modelo de eventos**: contrato `NormalizedEvent` (`occurred_at`,
  `category`, `payload`, `source`) y tabla `user_events` (índice por
  usuario/categoría/`occurred_at`). El `Connector` se generaliza a
  `Connector[RawT, OutT]` para que Steam siga dando items y ListenBrainz dé
  eventos.
- **D39 · Granularidad y resumen**: cada listen guarda artista + track + release;
  el resumen expone total de scrobbles, scrobbles de la ventana, **top artistas**
  y **top tracks** de los últimos 30 días (ventana por defecto), estrenando la
  consulta temporal. Álbumes se derivan del release cuando exista.
- **D40 · Refresco incremental (cierra D17)**: ListenBrainz acepta `min_ts`; el
  refresco trae solo listens posteriores al último `occurred_at` guardado y los
  añade (la llave de cambio es el timestamp del último listen).

Deuda: paginación de listens acotada por página en v1 (una pasada por refresco);
el histórico profundo se rellena en refrescos sucesivos.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [schema.py]** `NormalizedEvent` (evento con timestamp).
- [x] **Paso 2: [connectors/base.py]** `Connector[RawT, OutT]`; Steam pasa a
  `Connector[SteamRawData, NormalizedItem]`.
- [x] **Paso 3: [connectors/listenbrainz/client.py]** cliente de la API
  (`get_listens` con `min_ts`, throttle e inyección de httpx).
- [x] **Paso 4: [connectors/listenbrainz/connector.py]** normaliza listens →
  `NormalizedEvent` (artist/track/release + occurred_at).
- [x] **Paso 5: [music/store.py]** `EventStore` puerto + memoria +
  `SupabaseEventStore` (`user_events`), con estado de frescura reutilizando
  `SourceStatus`/`source_state`.
- [x] **Paso 6: [music/summary.py]** resumen con ventana (total, ventana, top
  artistas, top tracks).
- [x] **Paso 7: [music/service.py]** refresco incremental desde el último
  `occurred_at`.
- [x] **Paso 8: [music/router.py + deps.py]** `POST /sources/listenbrainz`
  (conectar por username + primer refresco), `POST /.../refresh`,
  `GET /sources/music`, `GET /context/music`.
- [x] **Paso 9: [mcp_server.py]** tools `music.summary`, `music.top_artists`,
  `music.recent` con auth y KB servidos.
- [x] **Paso 10: [registry.py + main.py + migración 0004]** registrar el
  conector, montar el router y crear `user_events`.
- [x] **Paso 11: [tests]** cliente (MockTransport), connector, store (memoria +
  PostgREST simulado), summary (ventana), service (fake), router (JWT), tools.

### 4. Reporte de Pruebas

**[APROBADO]** — ruff y mypy sin incidencias; pytest 106/106 (22 nuevos),
cobertura 94.2%. Secretos: ListenBrainz se lee por username público, sin
tokens; grep limpio. Idioma D19 correcto. Pendiente: cablear la web (Música
activa) y aplicar la migración 0004 en Supabase (por-revisar.md).
