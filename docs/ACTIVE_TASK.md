# ACTIVE_TASK — Generalización del contrato (Category, 9) + registry de conectores

Tarea: renombrar `MediaCategory` → `Category` ampliándolo a las 9 categorías del
catálogo (D27, ids del diseño) y añadir el registro de conectores (D21):
(categoría, proveedor) → clase de conector, con Steam registrado.

## 1. Contexto y Archivos Afectados

- `api/src/ethos_api/schema.py` — enum `Category` (9) y referencias.
- `api/src/ethos_api/connectors/base.py` — tipado con `Category`.
- `api/src/ethos_api/connectors/registry.py` — NUEVO: `ConnectorRegistry` + registro por defecto.
- `api/src/ethos_api/connectors/steam/connector.py` — import/uso de `Category`.
- `api/src/ethos_api/credentials/models.py` — `Category` en los modelos.
- Tests: `tests/connectors/test_steam_connector.py` (ajuste) y `tests/connectors/test_registry.py` (nuevo).

## 2. Evaluación Crítica

**Veredicto: bueno.** Ejecuta D21 y la parte de enum de D23/D27; la web enseña
el catálogo completo desde el día 1, así que retrasarlo encarecía cada tabla y
endpoint intermedio. Sin choques con PRD/arquitectura.

Opciones:
1. (Rec.) Ids del diseño como valores (`games, music, film, anime, fitness,
   books, places, food, board`) + registry de clases con registro explícito.
   Coherente con URLs, archivos de contexto y estado de la web.
2. Valores compuestos (`film_tv`, `board_games`): más descriptivos pero
   divergen de los ids que usa el diseño en todas partes.
3. Registry con auto-descubrimiento: magia innecesaria para 9 conectores.

Deuda prevista: el catálogo de UI (proveedor inicial + alternativas por
categoría) aún no vive en código — llegará con el endpoint de Fuentes; el
namespace MCP de Juegos de mesa (`tabletop.*`) difiere del id (`board`) y se
mapeará en la capa MCP (D28).

## 3. Plan de Acción Detallado

### Bloque A — Contrato
- [x] **Paso 1: [schema.py]** renombrar `MediaCategory` → `Category` con las 9
  categorías (ids del diseño) y actualizar `NormalizedItem` y docstrings.

### Bloque B — Conectores
- [x] **Paso 2: [connectors/base.py]** tipar `category: ClassVar[Category]`.
- [x] **Paso 3: [connectors/registry.py]** `ConnectorRegistry` con `register`
  (duplicado → `ValueError`), `get` (ausente → `LookupError`) y `providers`;
  instancia global `registry` con `SteamConnector` registrado.
- [x] **Paso 4: [connectors/steam/connector.py]** usar `Category.games`.

### Bloque C — Credenciales
- [x] **Paso 5: [credentials/models.py]** `Category` en input, credencial y resumen.

### Bloque D — Tests
- [x] **Paso 6: [tests/connectors/test_steam_connector.py]** imports y asserts a `Category`.
- [x] **Paso 7: [tests/connectors/test_registry.py]** NUEVO: enum con las 9;
  registro por defecto resuelve (games, steam); `get` inexistente →
  `LookupError`; duplicado → `ValueError`; `providers` por categoría.

## 4. Reporte de Pruebas

**[APROBADO]**

- Funcional: `Category` con los 9 ids del diseño (D27); el registry (D21)
  resuelve (games, steam) y rechaza duplicados/ausentes; las credenciales
  aceptan las 9 categorías.
- Idioma: identificadores en inglés; comentarios y docstrings en español.
- Secretos: grep limpio en lo modificado (solo la declaración `token: str`
  del modelo, sin valores).
- Stack (uv): ruff sin issues; mypy sin issues (31 archivos); pytest 31
  passed; cobertura 96.07% (umbral 85%).
