# Modelo de datos — Contexto

## 1. Contrato normalizado (transversal a todas las categorías)

Toda app de tracking describe lo mismo a alto nivel: una obra y la relación de la persona con ella. Se modelan en dos capas.

Capa universal (la relación, igual en todas las categorías):
- estado (en biblioteca / consumido / en progreso / en deseados / abandonado)
- calificación (normalizada 0-100, conservando el valor original)
- favorito
- fechas (agregado, iniciado, terminado)
- engagement (horas, número de reproducciones, etc., según la fuente)
- reseña, etiquetas

Capa específica del dominio (la obra):
- título, creadores (director / autor / artista / desarrollador), año
- external_ids: mapa de IDs canónicos por dominio (cine: TMDb/IMDb; libros: ISBN; música: MusicBrainz; juegos: Steam appid). Permite continuidad al cambiar de proveedor y deduplicación dentro de una fuente.
- extra: campos propios del tipo (runtime, géneros, plataformas, páginas, etc.)

Metadatos:
- source (conector que produjo el registro)
- provenance (de qué fuente vino cada campo) — alimenta la transparencia del dump
- schema_version (para evolucionar el contrato sin romper datos viejos)

## 2. Contrato de conector

Cada proveedor implementa una interfaz común:
- identidad (id, categoría, modo de ingesta, capacidades: qué campos puede llenar)
- detección (para autodetectar el archivo en imports)
- lectura (parsear archivo o llamar API → registros crudos)
- normalización (crudo → registro del esquema común)

Añadir un proveedor = implementar el conector, registrarlo y agregar fixtures de prueba.

## 3. Normalizaciones que cada conector resuelve

- Estados: traducir el vocabulario propio de cada app al enum común.
- Calificaciones: normalizar la escala a 0-100 conservando el original.

## 4. Slice de Steam (v1)

### Fuentes de datos (Steam Web API)
- Biblioteca, horas y última sesión: `GetOwnedGames`.
- Jugados recientes: `GetRecentlyPlayedGames`.
- Porcentaje de completado: derivado de logros desbloqueados / totales por juego (`GetPlayerAchievements` + esquema de logros). Se almacena solo el agregado, no el detalle de cada logro. Juegos sin logros: completado = N/A.
- Deseados (wishlist): endpoint de wishlist (requiere perfil público).
- Perfil: `GetPlayerSummaries`.

Conexión: "Sign in through Steam" (OpenID); el servidor obtiene el SteamID64 y usa su propia API key. Requisito: perfil y detalles de juego públicos; manejar el caso de perfil privado con un mensaje claro.

### Tablas (normalizadas e indexadas)

| Tabla | Contenido |
|-------|-----------|
| `games` | appid (ID canónico), nombre, géneros (diferido) |
| `user_games` | user_id, appid, horas_totales, horas_2sem, última_sesión, completado_pct, estado |
| `user_wishlist` | user_id, appid, prioridad / fecha agregado (según disponibilidad) |
| `user_profile_steam` | user_id, steamid, nombre, avatar |
| `source_state` | user_id, categoría, proveedor, modo, last_synced_at, estado |

Índices: `(user_id, última_sesión)`, `(user_id, horas_totales)`, `(user_id, completado_pct)`, `(user_id, appid)`.

### Diseño del MCP para juegos
- Resource `profile://games/summary`: resumen compacto (tamaño de biblioteca, total de horas, juegos top, completado medio, deseados destacados).
- Tools (pocas y parametrizadas):
  - `top_games(by="playtime"|"recent", limit)`
  - `recently_played(window)`
  - `search_games(query)`
  - `game_detail(juego)` — horas, completado, estado
  - `wishlist(limit)`
  - `games_by_completion(min_pct)`

Mantener el número total de tools bajo (la precisión del modelo al elegir herramienta cae pasadas ~25-30).

## 5. Frescura

`source_state.last_synced_at` por fuente alimenta el aviso de frescura en el dump y los estados del botón de refresco (inactivo / en cola / actualizando / error).
