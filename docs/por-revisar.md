# Por revisar — checklist para el usuario

Cosas que quedan en tus manos: configuración de infraestructura y verificación
visual en producción. efesto va añadiendo aquí lo que no puede hacer por ti.
Marca `[x]` conforme lo revises.

## Prueba end-to-end de Fase 1 (cuando estén las env vars)

- [ ] Inicia sesión, conecta Steam desde Fuentes, espera el refresco y revisa
  Inicio y el Detalle de Juegos con tus datos reales.
- [ ] En Conectar IA, genera el token, copia endpoint + token y prueba una
  consulta `games.summary` desde un cliente MCP (Claude Desktop u otro).
- [ ] Descarga `games.context.json` desde el Detalle de Juegos.

## Prueba end-to-end de Fase 2 · Música (tras aplicar la migración 0004)

- [ ] En Fuentes → Música (o Inicio → fila Música → "conéctala"), escribe tu
  usuario público de ListenBrainz, conéctalo y espera el refresco: el Detalle de
  Música debe mostrar escuchas, top artistas y top canciones de los últimos 30
  días.
- [ ] Comprueba que en Inicio la fila de Música aparece **activa** (con su número
  de escuchas) y que Fuentes la lista en "Activas" junto a Juegos.
- [ ] Prueba una consulta `music.top_artists` desde tu cliente MCP y descarga
  `music.context.json` desde el Detalle de Música.
- [ ] Nota de diseño a confirmar: la banda "El gusto en números" de Inicio
  sigue mostrando cifras de Juegos (su meta ya cuenta las fuentes activas); si
  quieres que mezcle métricas de música, dilo y lo ajustamos.

## Fase 3 · Cine y TV / Trakt

- [ ] **Registrar la app de Trakt y poblar `TRAKT_CLIENT_ID`** — crea una API
  app en Trakt (Settings → Your API Apps), copia su **Client ID** y ponlo en
  Render como `TRAKT_CLIENT_ID`. Sin esa key el conector no puede leer datos.
  El perfil de Trakt que conectes debe ser **público** (si no, el estado sale
  `private`).
- [ ] **Prueba end-to-end de Cine y TV** — en Fuentes o el Detalle de Cine y
  TV, conecta tu usuario de Trakt, espera el refresco y revisa horas, tops y
  vistos recientes; prueba `film.top_movies` por MCP y descarga
  `film.context.json`.

## Fase 3 · Anime y manga / AniList (sin keys que configurar)

- [ ] **Prueba end-to-end de Anime** — AniList no requiere key ni OAuth: en el
  Detalle de Anime y manga escribe tu usuario de AniList (listas públicas),
  espera el refresco y revisa episodios, nota media, mejor puntuados y en
  curso; prueba `anime.top_rated` por MCP y descarga `anime.context.json`.

## Fase 3 · Libros / Goodreads (import)

- [ ] **Prueba end-to-end de Libros** — exporta tu biblioteca de Goodreads
  (My Books → Import and export → Export Library), súbela en el Detalle de
  Libros y revisa leídos, páginas, leyendo ahora y autores; prueba
  `books.currently_reading` por MCP y descarga `books.context.json`. Un
  archivo que no sea el export debe rechazarse con guía (422).
- [ ] Nota: con las cinco categorías activas, Fuentes ya no muestra el grupo
  "En desarrollo" y el panorama de Inicio enseña las cinco filas (activas o
  apagadas). Confirma que te cuadra visualmente en producción.

- [ ] **OAuth Google en Supabase** (GitHub se retiró de la web, D26 revisada) —
  crear la app OAuth en Google Cloud Console con redirect URI
  `https://<tu-proyecto>.supabase.co/auth/v1/callback`, habilitar el proveedor
  Google (Authentication → Sign In / Providers) con su client id/secret, y en
  URL Configuration poner Site URL `https://<tu-web>` y añadir
  `https://<tu-web>/auth/callback` a las Redirect URLs. Hasta hacerlo, el
  botón "Continuar con Google" no completa el login. (Auth, D26)
- [ ] **Variables de entorno de la web** — poblar `NEXT_PUBLIC_SUPABASE_URL` y
  `NEXT_PUBLIC_SUPABASE_ANON_KEY` en Vercel (y en `web/.env.local` para
  desarrollo). Sin ellas, `/auth` lanza el error de configuración. (D26)
- [ ] **Redirects permitidos en Supabase Auth** — añadir a la allowlist de
  "Redirect URLs" tu dominio y `…/auth/callback` (incluye el flujo de
  recuperación `…/auth/callback?next=/auth/nueva-clave`). (D26)

## Decisiones que tomé por delegación (2026-07-03) — revísalas

- [ ] **D32** Wishlist de Steam sin títulos en v1 (solo conteo + appids por
  prioridad); la resolución de títulos queda diferida.
- [ ] **D33** Completado solo para el top 20 por horas en cada refresco
  (protege la cuota de la API key).
- [ ] **D34** Forma de `games.context.json`: resumen + top + recientes +
  wishlist, sin histórico de eventos en v1.
- [ ] **D35** Persistencia en memoria tras puerto: los datos del backend se
  pierden al redeploy hasta el respaldo Supabase (único pendiente de Fase 1).
- [ ] **D36** Refresco con BackgroundTasks y estados de frescura; cola durable
  después. Perfil privado de Steam → estado `private`.

## Verificación visual en producción

- [ ] **Auth** — `/auth`: alternar login/registro, mostrar/ocultar contraseña,
  validaciones (correo, mínimo 8), toggle de tema; `/auth/recuperar`
  y `/auth/nueva-clave`. (D26)
- [ ] **Shell de la app** — `/app`: barra lateral (Inicio · Fuentes · Conectar
  IA · Ayuda), resaltado del activo, badge pulsante en "Conectar IA", engrane →
  Ajustes, header por pantalla, y el comportamiento responsivo (barra → top bar
  en pantallas estrechas).
- [ ] **Inicio** — `/app`: banner de IA, stat band "El gusto en números",
  panorama (Juegos activa + cuatro "en desarrollo") y actividad reciente. Ojo:
  los números y la actividad son **datos de ejemplo** del prototipo hasta que
  esté el backend de Steam; confirma que te parece bien mostrarlos así de
  momento.
- [ ] **Detalle de categoría** — `/app/categoria/games` (Juegos): status strip,
  stat band con sparkline, Destacados/Reciente/Listas, botón Refrescar y modal
  "Descargar contexto" (pestañas JSON/MCP, copiar, descargar). Y una categoría
  en desarrollo, p. ej. `/app/categoria/music`.
- [ ] **Fuentes** — `/app/fuentes`: resumen, grupo Activas (Juegos) y grupo En
  desarrollo (las cuatro).
- [ ] **Conectar IA** — `/app/conectar-ia`: endpoint/token (placeholder), tres
  pasos y el playground (toca una consulta o escribe la tuya; mira el panel "Lo
  que pasa por detrás"). Ojo: endpoint/token/estado son **simulados** hasta el
  backend del MCP.
- [ ] **Ayuda** — `/app/ayuda`: FAQ (acordeón) y el envío de sugerencias
  (efímero; el envío real es Fase 4).
- [ ] **Ajustes** — `/app/ajustes`: Apariencia cambia el tema de verdad
  (claro/oscuro/sistema). Perfil y Zona de peligro son **efímeros/simulados**
  hasta el backend (persistencia y borrado con deshacer, Fase 4).
