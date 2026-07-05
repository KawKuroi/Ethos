# Registro de decisiones — Contexto

Cada entrada: decisión, motivo y estado.

## D1 — Arquitectura híbrida Python + TS
Python para pipeline y MCP; TypeScript para la web y los gráficos. Cada pieza en el lenguaje donde es más fuerte, y refuerza el perfil de datos. Estado: firme.

## D2 — Todo hospedado, nada local-first
La aplicación y el servidor MCP corren en la nube; el usuario no instala nada. Motivo: comodidad para cualquier usuario. Implica custodiar credenciales y datos. Estado: firme.

## D3 — Stack de hospedaje
Vercel (web) + un único servicio en Render combinando backend y MCP + Supabase (datos, auth, secretos, cola). Motivo: 0 USD/mes sin tarjeta. Estado: firme, con mitigaciones de cold start.

## D4 — Una fuente por categoría, intercambiable
El usuario elige un proveedor por categoría y puede cambiarlo. Motivo: simplicidad de UI y de lógica; elimina la fusión simultánea entre proveedores. Estado: firme.

## D5 — Al cambiar o desconectar una fuente, preguntar al usuario
Se le pregunta si conserva el histórico (inactivo) o lo reemplaza por el nuevo proveedor. Motivo: control del usuario. Implica soportar borrado suave. Estado: firme.

## D6 — Conexión por API o por import, a elección del usuario
Donde el proveedor tiene API amable se conecta directo; si no, se sube el export. Motivo: muchas plataformas cerraron sus APIs (Goodreads, Spotify, Letterboxd), así que el import es la base universal. Estado: firme.

## D7 — Música: ListenBrainz como proveedor principal
Reemplaza a Last.fm. Motivo: API abierta, listens con timestamp, datos CC0, sin riesgo de lock-down. Estado: firme.

## D8 — Auth del MCP por token simple
Token único por usuario validado en middleware. Motivo: rápido de implementar. Migrable a OAuth 2.1 más adelante. Estado: firme para v1.

## D9 — Tokens de terceros cifrados a nivel de app
Cifrado simétrico con la llave en el secret manager. Motivo: control y simplicidad. Mejora futura: envelope encryption con KMS. Estado: firme.

## D10 — Refresco asíncrono con Supabase Queues
El botón encola, un worker procesa, se actualiza la frescura. Motivo: no bloquear la UI y evitar Redis u otros servicios. Estado: firme.

## D11 — Primer slice vertical: Juegos / Steam
Construir una categoría completa de punta a punta antes de replicar. Motivo: menor riesgo, demostrable rápido, valida la arquitectura. Steam tiene la API más limpia. Estado: firme.

## D12 — Conexión de Steam por OpenID
"Sign in through Steam", un clic. Motivo: la mejor UX sin pedir claves al usuario. Estado: firme.

## D13 — Alcance de datos de Steam en v1
Biblioteca, deseados, horas, porcentaje de completado agregado por juego, y perfil. Sin detalle de logros individuales. Motivo: el detalle de logros no es prioritario para el propósito. Estado: firme.

## D14 — Monorepo
Un repositorio con carpetas por capa. Motivo: dev solo, cambios atómicos, tipos compartidos. Estado: firme.

## D15 — Tests obligatorios en todas las capas
Conectores (golden-file), normalización, API, tools del MCP (en memoria), web (componentes + E2E), en CI. Estado: firme.

## D16 — Géneros de juegos: diferidos (por defecto, a confirmar)
Steam no da géneros en la biblioteca; enriquecerlos requiere otra fuente. Por defecto se difieren a una fase posterior. Estado: por confirmar.

## D17 — Refresco incremental (por defecto, a confirmar)
Re-consultar solo lo que cambió desde el último sync. Estado: por confirmar la llave de cambio por proveedor.

## D18 — Framework web: Next.js (App Router)
Se resuelve la opción abierta "Next.js o Astro" a favor de Next.js. Motivo: mejor ajuste para auth (Supabase), dashboards interactivos y la guía "conecta tu IA"; ecosistema Vercel nativo. Estado: firme (la mención original a Recharts queda sustituida por D29).

## D19 — Idioma del código: identificadores en inglés
Identificadores (variables, funciones, tablas, columnas, claves) en inglés; comentarios, docs, commits y textos de UI en español. Motivo: convención estándar de Python/TS, evita acentos en SQL/código y mantenibilidad. Los nombres en español de los docs de datos son descriptivos, no DDL literal. Estado: firme. Detalle en `global.md`.

## D20 — Sesión de usuario y credenciales de terceros cifradas
Supabase Auth para la sesión de la app. Las credenciales/keys de terceros que aporta el usuario se guardan en una tabla `user_credentials` cifradas a nivel de app (Fernet: AES-128-CBC + HMAC), con la llave en el secret manager y RLS owner-only. Se descifran solo en memoria al llamar la API; nunca viajan al cliente. Refuerza D9. Estado: firme (diseño); implementación pendiente.

## D21 — Registro de conectores para extender categorías y proveedores
Un registro asocia (categoría, proveedor) → conector, modo de ingesta y `capabilities`. Las capas río abajo (normalización, persistencia, MCP, web) resuelven por el registro; añadir una categoría o proveedor es implementar y registrar un conector, sin tocar nada más. Estado: firme.

## D22 — Auth del MCP antes de exponer tools de datos
Las tools que exponen datos del usuario requieren el middleware de token por usuario (D8). Mientras no exista, solo se publican tools no sensibles (hoy `ping`); el endpoint `/mcp` no sirve datos sin auth. Guardrail de seguridad. Estado: firme.

## D23 — Catálogo de categorías y generalización del contrato (por confirmar)
Categorías objetivo (9) con su proveedor inicial: Juegos/Steam (API), Música/ListenBrainz (API), Cine y TV/Trakt (API), Anime y manga/AniList (API), Actividad física/Strava (API), Libros/Goodreads (import), Lugares/Swarm (API), Comida/Beli (import), Juegos de mesa/BoardGameGeek (import). La mayoría encaja en "obra + relación" (rating, estado, engagement); Lugares y Comida tratando el sitio o el plato como obra. Actividad física (Strava) es de tipo evento/métrica (distancia, duración) y no es una "obra": el contrato normalizado deberá admitir también esa forma. El enum `MediaCategory` se renombrará a `Category` y se ampliará. Estado: catálogo fijado en 6 por D27 y ajustado a 5 por D31; la forma evento/métrica deja de ser necesaria al salir Actividad física (todo el catálogo encaja en "obra + relación").

## D24 — Dos salidas del contexto: descarga y MCP
El contexto para la IA se entrega de dos formas equivalentes en origen: archivos descargables por categoría (`<categoria>.context.json`, vía `GET /context/{category}`) y el servidor MCP en vivo. Motivo: el diseño final las trata como par de primera clase ("El panel" / "Servidor MCP" + "Descargar contexto" en cada categoría); la descarga sirve a cualquier IA sin soporte MCP. Sustituye la idea previa de que el MCP era la única vía. Estado: firme.

## D25 — El diseño de Claude Design es la fuente de verdad de la UI
Proyecto "Prototipo creativo de aplicación" (`c3e4858c-944b-427a-b1b7-6c327a8a1dd1`): app, auth y landing en alta fidelidad (tokens, textos, animaciones e interacciones finales). Cualquier duda de implementación se resuelve mirando el prototipo, no los docs; `design.md` es solo el resumen. Estado: firme.

## D26 — Auth de la app: correo + Google + GitHub (Supabase Auth)
Login/registro con correo y contraseña (mínimo 8, recuperación) y OAuth de Google y GitHub, según el diseño de auth. Steam NO es login de la app: su OpenID es el flujo de conexión de la fuente de Juegos (D12). Estado: firme.

## D27 — Catálogo de 6 categorías con estados y despliegue secuencial
El catálogo activo son 6 categorías: Juegos, Música, Cine y TV, Anime y manga, Actividad física y Libros (alternativas por categoría en `architecture.md` 4.1). Diferidas hasta nueva decisión (revisión del 2026-07-03: "lo básico y más popular primero"): Lugares, Comida y Juegos de mesa; Pódcasts y YouTube del prototipo también quedan fuera. Cada categoría tiene estado visible: activa, apagada (sin datos) o en desarrollo (no activable). El despliegue es secuencial: se construye una categoría de punta a punta, se prueba y se confirma antes de pasar a la siguiente; las no implementadas aparecen "en desarrollo" (en la v1, todas salvo Juegos). Amplía D23. Estado: firme; ajustada por D31 (Actividad física retirada, catálogo de 5). Alternativas depuradas tras la investigación de fuentes del 2026-07-03: Juegos queda Steam + Xbox/PlayStation (APIs no oficiales) + GOG (import), fuera Epic; los modos por proveedor se detallan en `architecture.md` 4.1.

## D28 — Tools del MCP con namespace por categoría
Las tools se nombran `<categoria>.<accion>` (`games.top_by_hours`, `music.recent`, `books.currently_reading`, `<categoria>.summary`…), más `profile.search` global. Cada respuesta reporta los KB servidos frente al contexto total ("0,4 KB de 84 KB"), métrica que la web enseña en el playground. Motivo: escala por categorías manteniendo pocas tools por dominio y hace tangible el valor "consulta acotada". Estado: firme.

## D29 — Web fiel al diseño: tokens CSS + CSS Modules, SVG propio, sin Recharts
El prototipo está expresado en CSS variables, estilos inline y SVG simples (sparklines, barras). La web se implementa traduciendo eso directo: tokens como CSS variables globales, CSS Modules, componentes de gráfico propios, `next/font` para Bricolage Grotesque + Hanken Grotesk y `next-themes` para claro/oscuro/sistema. Recharts (D18) queda descartado: no hay gráficos que lo necesiten y pelearía contra la fidelidad. Estado: firme.

## D30 — Hardening de la API contra abuso
Middlewares ASGI propios en memoria: rate limit por IP (ventana deslizante, 429 + Retry-After, `/health` exento), límite de tamaño de cuerpo (413) y cabeceras de seguridad; más CORS restringido al origen de la web, TrustedHost y docs interactivos apagados en producción. uvicorn corre con `--proxy-headers` para ver la IP real tras el proxy de Render. El cliente de Steam lleva throttle de intervalo mínimo para cuidar la cuota de la API key. ASGI puro (sin BaseHTTPMiddleware) para no romper el SSE del MCP; cero dependencias nuevas. Si el backend escala a varias réplicas, el limitador migra a un backend compartido (p. ej. Redis). Estado: firme.

## D31 — Actividad física sale del catálogo
La categoría se retira; el catálogo activo queda en 5 (Juegos, Música, Cine y TV, Anime y manga, Libros). Motivo (investigación de fuentes 2026-07-03): no existe fuente viable — el acuerdo de API de Strava (2024, vigente) prohíbe usar sus datos en modelos de IA, justo el propósito de Ethos; Garmin no acepta desarrolladores personales (exige entidad legal y el programa está en pausa); la Web API de Fitbit se apaga en septiembre de 2026 y su sucesora (Google Health API) exige verificación restringida de Google inviable para un proyecto a costo 0. Beneficio lateral: desaparece la única categoría de tipo evento/métrica, así que el contrato normalizado se queda en "obra + relación" (simplifica D23). Se reevaluará solo si aparece una fuente abierta (p. ej. import de Apple Health). Estado: firme.

## D32 — Wishlist de Steam: IWishlistService, títulos diferidos
La wishlist se lee de `IWishlistService/GetWishlist/v1` (appid, prioridad, fecha de añadido) y se normaliza como items `status=wishlist`. La respuesta no trae títulos y resolverlos exige una llamada de store por juego: en v1 la wishlist viaja como conteo + appids priorizados; la resolución de títulos queda diferida (candidata a la caché de catálogos globales compartida entre usuarios). Decisión delegada por el usuario (2026-07-03). Estado: firme.

## D33 — Completado agregado con presupuesto fijo
`GetPlayerAchievements` es una llamada por juego. Para no quemar la cuota de la API key, el completado se calcula solo para el top 20 por horas en cada refresco, protegido por el throttle del cliente (D30). Juegos sin logros o con error puntual quedan sin porcentaje; el agregado del resumen es la media de los calculados. Resuelve el pendiente de límites de tasa. Decisión delegada por el usuario. Estado: firme.

## D34 — Forma del contexto de juegos (concreta D24)
`games.context.json` = `{namespace, provider, generated_at, profile, summary{games, hours, wishlisted, avg_completion_pct, last_synced_at}, top_by_hours[10], recently_played, wishlist{count, top_priority_appids}}`. Es la misma información en origen que sirven las tools del MCP. Sin histórico de eventos en v1: el modelo de eventos con timestamp llega con Música (Fase 2) y entonces se revisará qué histórico incluye la descarga. Decisión delegada por el usuario. Estado: firme.

## D35 — Persistencia del slice tras puerto; Supabase por PostgREST
Los datos de juegos, las credenciales y los tokens del MCP persisten tras puertos (`Protocol`) con dos implementaciones: memoria indexada (tests y desarrollo) y Supabase. La migración 0003 crea `user_items` (genérica por categoría: Música la reutiliza en Fase 2, con `payload` jsonb = `NormalizedItem` y columnas extraídas para indexar) y `mcp_tokens`, y amplía `source_state` (estado `private`, `detail`, `provider_profile`). Los repos Supabase hablan con PostgREST usando la service_role key: el backend es la capa de confianza (autentica por JWT y acota por `user_id`) y las políticas RLS owner-only bloquean el acceso directo de cualquier otro cliente. La selección memoria/Supabase es automática según el entorno. Decisión delegada por el usuario. Estado: firme.

## D36 — Refresco asíncrono v1 con BackgroundTasks y estados de frescura
El refresco corre en segundo plano con `BackgroundTasks` de FastAPI y deja estado explícito por usuario: `never/syncing/fresh/private/error` + `synced_at` (stale se deriva por edad). Perfil de Steam privado → estado `private` con guía para la web. La cola durable (Supabase Queues) llega con la infra de D35; el refresco incremental (D17) sigue abierto para Fase 2. Decisión delegada por el usuario. Estado: firme.

## D37 — Conexión de Música: ListenBrainz por username público
La fuente de Música se lee de ListenBrainz por el username público del usuario (`GET /1/user/{user}/listens`); no requiere OAuth ni token. El username se guarda como credencial del proveedor `listenbrainz` (categoría music), cifrado como el steamid (D20). Decisión delegada por el usuario (2026-07-04). Estado: firme.

## D38 — Modelo de eventos con timestamp
Las fuentes de tipo evento (Música y futuras) usan `NormalizedEvent` (`occurred_at`, `category`, `payload`, `source`) en vez de `NormalizedItem` ("obra + relación"). El `Connector` se generaliza a `Connector[RawT, OutT]` (Steam da items, ListenBrainz da eventos). Los eventos persisten en `user_events` (migración 0004) con índice (user_id, category, occurred_at desc) para las consultas por ventana. El estado de frescura se comparte en `sources_status.py`. Decisión delegada. Estado: firme.

## D39 — Granularidad y resumen de Música
Cada listen guarda artista + track (+ release cuando exista). El resumen (`build_music_summary`) expone total de scrobbles, scrobbles de la ventana, top artistas y top tracks de los últimos 30 días (ventana por defecto), estrenando la consulta temporal real. Tools del MCP: `music.summary`, `music.top_artists`, `music.recent` (+ resource `ethos://music/summary`). Decisión delegada. Estado: firme.

## D40 — Refresco incremental de Música (cierra D17)
El refresco trae solo los listens posteriores al último `occurred_at` guardado (`min_ts` de ListenBrainz) y los añade; la llave de cambio es el timestamp del último listen. Una pasada por refresco en v1 (el histórico profundo se rellena en refrescos sucesivos). Resuelve el pendiente D17 para fuentes de evento. Decisión delegada. Estado: firme.
