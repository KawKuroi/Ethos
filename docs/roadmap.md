# Roadmap — Contexto

Fases de construcción. Cada tarea se marca `[x]` al completarse; al cerrarse una
fase entera se mueve a `## Histórico de fases completadas`.

## Fase 0 — Fundación

- [ ] Monorepo con `/web` (TS) y `/api` (Python, incluye MCP).
- [ ] Supabase: proyecto, Auth, esquema base, Row-Level Security.
- [ ] Servicio en Render (backend + MCP combinados) y web en Vercel, desplegando un esqueleto.
- [ ] Keep-alive ping configurado.
- [ ] Secret manager con la llave de cifrado y la Steam API key.
- [x] CI en GitHub Actions con la estructura de tests vacía pero corriendo.

## Fase 1 — Slice vertical: Juegos / Steam (la v1)

- [ ] Login con Steam (OpenID) y manejo de perfil privado.
- [ ] Conector de Steam: biblioteca, deseados, horas, completado agregado, perfil.
- [ ] Normalización al esquema común y persistencia indexada.
- [ ] Generador del resumen de juegos.
- [ ] Servidor MCP: resource de resumen + tools de juegos.
- [ ] Web: panel de estadísticas (dump) de juegos.
- [ ] Refresco asíncrono con cola y estados de frescura.
- [ ] Sección de ayuda y guía "conecta tu IA".
- [ ] Tests de todas las capas pasando en CI.

## Fase 2 — Segunda categoría: Música / ListenBrainz

- [ ] Conector de ListenBrainz por API (listens con timestamp).
- [ ] Estrena la consulta temporal real ("más escuchadas en los últimos 30 días").
- [ ] Modelo de eventos con timestamp y sus índices.
- [ ] Tools del MCP para música (artistas, álbumes, tracks, ventanas temporales).

## Fase 3 — Categorías restantes

- [ ] Cine/TV: Trakt (API) y Letterboxd (import).
- [ ] Libros: Goodreads / StoryGraph (import) y Hardcover (API).
- [ ] Modo import genérico con autodetección de archivo.

## Fase 4 — Pulido y robustez

- [ ] Migración del auth del MCP a OAuth 2.1 (si se requiere).
- [ ] Enriquecimiento de géneros de juegos.
- [ ] Envelope encryption con KMS (si se requiere).
- [ ] Opción de mover el backend a Cloud Run para eliminar cold starts.
- [ ] Empaquetado y distribución pulidos; objetivos de cobertura de tests.

## Pendientes y decisiones por resolver

- Nombre definitivo del proyecto (provisional: Ethos).
- Géneros de juegos: fuente de enriquecimiento (store API de Steam vs IGDB/RAWG). (D16)
- Refresco incremental: llave de cambio por proveedor. (D17)
- Esquema fino del perfil por categoría: qué va en el resumen (resource) vs en las tools, para música, cine y libros.
- Granularidad de música (artista / álbum / track) — por defecto los tres; confirmar el corte del resumen.
- Wishlist de Steam: campos disponibles (prioridad, fecha agregado, precio) y endpoint exacto.
- Manejo de límites de tasa de Steam al calcular el completado (una llamada por juego).
- Política de retención del histórico inactivo (cuánto tiempo se conserva).
- Diseño detallado de la guía "conecta tu IA" para usuarios no técnicos (con Claude Design).
- Objetivos concretos de cobertura de tests y umbrales de CI.
- Estrategia de caché de catálogos globales (esquema de logros, metadatos de juegos) compartidos entre usuarios.

## Histórico de fases completadas

_(Aún ninguna. Las fases cerradas se moverán aquí con un resumen breve.)_
