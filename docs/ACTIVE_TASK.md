# ACTIVE_TASK — Fase 1 (backend, parte 1): conector de Steam + contrato normalizado

Tarea: implementar el contrato de datos normalizado (transversal a categorías),
la interfaz de conector, y el conector de Steam para su núcleo (biblioteca con
horas, jugados recientes y perfil), con normalización al esquema común y tests
de fixtures (golden-file). Sin web, sin persistencia y sin las piezas con
decisiones abiertas.

## 1. Contexto y Archivos Afectados

Trabajo dentro de `/api` (Python). No hay aún capa de datos ni conectores: se
crea un módulo nuevo, por lo que el límite de 5 archivos del Lector no aplica
(creación de estructura, no lectura de código existente). Archivos:

- `api/src/ethos_api/schema.py` — contrato normalizado (enums + modelos Pydantic).
- `api/src/ethos_api/connectors/__init__.py`
- `api/src/ethos_api/connectors/base.py` — interfaz de conector (identidad + normalización).
- `api/src/ethos_api/connectors/steam/__init__.py`
- `api/src/ethos_api/connectors/steam/client.py` — cliente HTTP de la Steam Web API.
- `api/src/ethos_api/connectors/steam/connector.py` — conector: identidad + normalización.
- `api/pyproject.toml` — añadir `httpx` a dependencias de runtime (hoy solo dev).
- `api/tests/connectors/__init__.py`
- `api/tests/connectors/test_steam_connector.py` — normalización contra fixtures.
- `api/tests/connectors/test_steam_client.py` — cliente con `httpx.MockTransport`.
- `api/tests/fixtures/steam_owned_games.json`
- `api/tests/fixtures/steam_player_summary.json`
- `api/tests/fixtures/steam_recently_played.json`

Fuente: `data-model.md` (secciones 1, 2 y 4). Endpoints cubiertos:
`GetOwnedGames`, `GetRecentlyPlayedGames`, `GetPlayerSummaries`.

Diferido (no inventar / depende de otras piezas):
- Wishlist y completado% por logros — decisiones abiertas (campos, rate limits).
- Persistencia indexada en Postgres — necesita la migración de Fase 1 y Supabase real.
- Login OpenID de Steam — auth, entrelazado con la web.

## 2. Evaluación Crítica

**Veredicto: viable / bueno.** Es el cimiento del slice de juegos y no depende de
cuentas externas ni de la web: se valida con fixtures. Respeta `data-model.md`
(el conector mapea crudo → contrato común, desacoplando las capas de arriba) y
la decisión D15 (conectores con golden-file). Sin choques con PRD/arquitectura.

Decisiones con trade-off (recomendada marcada):

1. **Objetivo de la normalización**: contrato genérico vs modelos Steam-específicos.
   - (Rec.) `NormalizedItem` genérico (capa universal + obra + metadatos) → las
     capas posteriores no dependen del origen (lo pide `data-model.md`).
   - Modelos solo-Steam → más simples ahora, pero acoplan y rompen el contrato.

2. **Cliente HTTP**: añadir `httpx` (runtime) vs `urllib` de la stdlib.
   - (Rec.) `httpx`: testeable con `MockTransport` sin red, ergonómico, estándar
     del ecosistema. Coste: una dependencia más.
   - `urllib`: sin dependencia, pero verboso y difícil de testear.

3. **Base del conector**: `Protocol` vs `ABC` genérico.
   - (Rec.) `ABC` genérico (`Connector[RawT]`) con identidad como `ClassVar` y
     `normalize` abstracto tipado → fuerza el contrato y mypy lo valida.
   - `Protocol` → más laxo; no obliga a implementar.

**Deuda técnica prevista (concreta):**
- *Sin persistencia*: los `NormalizedItem` se producen pero no se guardan; la
  persistencia indexada es la siguiente tarea (requiere migración + Supabase).
- *Campos no provistos por Steam*: `GetOwnedGames` no da creadores, año ni
  calificación; quedan vacíos y `capabilities` lo declara (transparencia).
- *Fixtures estáticas*: si Steam cambia su API, los golden-file se desactualizan;
  riesgo aceptado (D15 manda golden-file).
- *Errores HTTP / perfil privado*: el cliente lanzará un error claro, pero el
  manejo de UX de "perfil privado" es de la web (diferido).

## 3. Plan de Acción Detallado

### Bloque A — Contrato normalizado
- [x] **Paso 1: [api/src/ethos_api/schema.py]** enums `MediaCategory`,
  `ItemStatus`, `IngestMode`; modelos Pydantic `Work` (title, creators, year,
  external_ids, extra) y `NormalizedItem` (capa universal: status, rating
  normalizado 0-100 + original, favorite, fechas, engagement, review, tags;
  más `work` y metadatos: source, provenance, schema_version).

### Bloque B — Interfaz de conector
- [x] **Paso 2: [api/src/ethos_api/connectors/__init__.py]** paquete.
- [x] **Paso 3: [api/src/ethos_api/connectors/base.py]** `Connector[RawT]` (ABC
  genérico) con `id`, `category`, `ingest_mode`, `capabilities` como `ClassVar`
  y `normalize(raw: RawT) -> list[NormalizedItem]` abstracto.

### Bloque C — Cliente Steam
- [x] **Paso 4: [api/src/ethos_api/connectors/steam/__init__.py]** paquete.
- [x] **Paso 5: [api/src/ethos_api/connectors/steam/client.py]** `SteamApiClient`
  (httpx) con `api_key` inyectable y transporte inyectable para tests:
  `get_owned_games(steamid)`, `get_recently_played(steamid)`,
  `get_player_summary(steamid)`; error claro ante respuesta no-200.

### Bloque D — Conector y normalización
- [x] **Paso 6: [api/src/ethos_api/connectors/steam/connector.py]** `SteamRawData`
  (owned/recent/profile) y `SteamConnector(Connector[SteamRawData])`: identidad
  (`id="steam"`, `category=games`, `ingest_mode=api`, `capabilities`), y
  `normalize` que mapea juegos a `NormalizedItem` (status `in_library`,
  engagement con minutos jugados totales y de 2 semanas, `external_ids` con
  `steam_appid`, `extra` con `last_played_at`), fusionando jugados recientes.

### Bloque E — Dependencia
- [x] **Paso 7: [api/pyproject.toml]** mover/añadir `httpx` a `dependencies`
  (runtime); mantenerlo disponible para tests.

### Bloque F — Tests y fixtures
- [x] **Paso 8: [api/tests/fixtures/steam_owned_games.json]** respuesta de muestra.
- [x] **Paso 9: [api/tests/fixtures/steam_player_summary.json]** respuesta de muestra.
- [x] **Paso 10: [api/tests/fixtures/steam_recently_played.json]** respuesta de muestra.
- [x] **Paso 11: [api/tests/connectors/__init__.py]** paquete de tests.
- [x] **Paso 12: [api/tests/connectors/test_steam_client.py]** el cliente parsea
  las respuestas usando `httpx.MockTransport` (sin red) y lanza error en no-200.
- [x] **Paso 13: [api/tests/connectors/test_steam_connector.py]** la
  normalización produce los `NormalizedItem` esperados desde las fixtures
  (golden-file): conteo, appids, minutos, status y engagement.

## 4. Reporte de Pruebas

**[APROBADO]**

- Cumplimiento funcional: contrato normalizado (`schema.py`), interfaz de
  conector y conector de Steam (owned games, jugados recientes, perfil) con
  normalización a `NormalizedItem`; cubre lo planeado.
- Idioma del código: identificadores en inglés, comentarios/docstrings en
  español (conforme a `global.md`).
- Secretos: grep sin coincidencias en `/api`.
- Verificación de stack (uv): `ruff check` sin issues; `mypy` sin issues
  (16 archivos); `pytest` 8 passed.
- Incidencias resueltas: ruff señaló modernizaciones de Python 3.12 (UP042 →
  `StrEnum`, UP046 → genéricos PEP 695 `Connector[RawT]`, UP017 →
  `datetime.UTC`); aplicadas y reverificado en verde.
