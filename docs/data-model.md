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
- provenance (de qué fuente vino cada campo) — alimenta la transparencia del panel
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

## 4. Contexto descargable (D24)

Un archivo por categoría, `<categoria>.context.json`, generado del almacén:

```json
{
  "namespace": "games.*",
  "provider": "Steam",
  "updated": "2026-06-30T09:12Z",
  "summary": { "juegos": "312", "horas": "1.840", "deseados": "47" },
  "top_por_horas": [ { "rank": 1, "name": "…", "value": "…", "tag": "…" } ],
  "tags": ["…"]
}
```

La vista previa de la web enseña este fragmento; el archivo completo incluye
además el histórico normalizado de la categoría. Forma exacta por afinar al
implementar el generador.

## 5. Slice de Steam (v1)

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

### Diseño del MCP para juegos (D28)

- Resource `profile://games/summary`: resumen compacto (tamaño de biblioteca, total de horas, juegos top, completado medio, deseados destacados).
- Tools (pocas y parametrizadas, namespace `games.*`):
  - `games.summary()` — el resumen como tool
  - `games.top_by_hours(limit)` y `games.top(by="playtime"|"recent", limit)`
  - `games.recent(window)`
  - `games.search(query)`
  - `games.detail(juego)` — horas, completado, estado
  - `games.wishlist(limit)`
  - `games.by_completion(min_pct)`

Global (transversal): `profile.search(q)` — localiza en qué categoría vive
algo. Mantener el número total de tools bajo (la precisión del modelo al
elegir herramienta cae pasadas ~25-30). Cada respuesta reporta los KB servidos
frente al tamaño total del contexto de la categoría.

## 6. Frescura y salud

- `source_state.last_synced_at` por fuente alimenta la etiqueta de frescura (fresh / stale / syncing) y los estados del botón de refresco (inactivo / en cola / actualizando / error).
- Salud derivada por fuente (para Fuentes e Inicio): error de sync > requiere atención (warn o stale) > operativa.
- Alertas por fuente con nivel (info / warn / error), texto, fecha y acción opcional (p. ej. "Renovar", "Reintentar"). Las no-info se agregan en Inicio.

## 7. Cuenta, sesión y credenciales

Sesión con Supabase Auth (correo/contraseña, Google, GitHub — D26).

Tabla `user_credentials` (D20) para "guardar las APIs" del usuario:

| Columna | Contenido |
|---------|-----------|
| user_id | dueño (FK a `auth.users`) |
| category | categoría (games, music, ...) |
| provider | proveedor (steam, listenbrainz, ...) |
| encrypted_token | credencial cifrada a nivel de app (Fernet/AES-GCM) |
| created_at / updated_at | timestamps |

Una credencial por `(user_id, provider)`. RLS owner-only (`auth.uid() = user_id`).
La llave de cifrado vive en el secret manager, nunca en la BD ni en el repo; el
texto plano solo existe en memoria al llamar la API. (D9, D20)

Perfil de usuario (`profiles`): nombre visible, handle y zona horaria (para
fechar sincronizaciones y actividad). Token del MCP por usuario, independiente
de las credenciales de terceros.

Sugerencias (`suggestions`): user_id opcional, categoría (General o una del
catálogo), tipo (`idea` / `provider` / `bug`), texto, created_at. Alimentada
desde Ayuda y desde la landing.

Borrado: "eliminar datos" limpia el contexto del usuario conservando la
cuenta; "eliminar cuenta" marca borrado diferido (30 días para deshacer vía
correo) antes de la purga definitiva.

## 8. Catálogo de categorías

Nueve categorías (D27), cada una con un proveedor activo intercambiable
(D4/D6) y estado activa / apagada / en desarrollo: Juegos, Música, Cine y TV,
Anime y manga, Actividad física, Libros, Lugares, Comida (solo import) y
Juegos de mesa (solo import). Se habilitan secuencialmente: las no
implementadas se muestran "en desarrollo" (en la v1, todas salvo Juegos). El
enum del contrato (`MediaCategory`) se generaliza a `Category` y se amplía a
las nueve. Detalle del catálogo en `architecture.md` 4.1 y de la
generalización del contrato (p. ej. Actividad física como evento/métrica) en
D23.
