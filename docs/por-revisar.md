# Por revisar — checklist para el usuario

Lo que queda en tus manos, en dos bloques: **Bloqueantes** (sin esto hay
partes del producto que no funcionan) y **Para ir revisando** (verificaciones
y decisiones sin prisa). efesto añade aquí lo que no puede hacer por ti;
marca `[x]` conforme lo resuelvas y lo movemos a Hecho.

## Bloqueantes — configuración que detiene el flujo

### Keys y variables de entorno

- [ ] **`TRAKT_CLIENT_ID` en Render** — crea una API app en Trakt (Settings →
  Your API Apps) y copia su Client ID. Sin la key, el conector de Cine y TV no
  puede leer datos. El perfil de Trakt que conectes debe ser público (si no,
  el estado sale `private`).
- [ ] **Supabase en la web** — `NEXT_PUBLIC_SUPABASE_URL` y
  `NEXT_PUBLIC_SUPABASE_ANON_KEY` en Vercel y en `web/.env.local` para
  desarrollo (verificado 2026-07-07: `web/.env.local` no existe todavía). Sin
  ellas, `/auth` lanza el error de configuración. (D26)
- [ ] **Env vars del blueprint en Render** — el blueprint ya declara
  `PUBLIC_BASE_URL` y `WEB_BASE_URL` con sus valores (issuer OAuth del MCP y
  página de consentimiento, D56), pero los blueprints existentes no añaden
  env vars solos: revisa en el dashboard que estén pobladas, junto con
  `TRAKT_CLIENT_ID` y las SMTP si las usas.

### Supabase Auth (D26)

- [ ] **OAuth Google** — crea la app OAuth en Google Cloud Console con
  redirect URI `https://<tu-proyecto>.supabase.co/auth/v1/callback` y
  habilita el proveedor Google (Authentication → Sign In / Providers) con su
  client id/secret. Hasta entonces, "Continuar con Google" no completa el
  login. (GitHub se retiró de la web.)
- [ ] **URL Configuration** — Site URL = `https://<tu-web>` (hoy está en
  localhost: por eso la confirmación te llevó a
  `http://localhost:3000/?code=…`) y añade a Redirect URLs
  `https://<tu-web>/auth` (confirmación de correo, va al login) y
  `https://<tu-web>/auth/callback` (OAuth y recuperación); en desarrollo,
  las mismas con `http://localhost:3000`.

### Jobs y monitores

- [ ] **Job de purga de cuentas (D53)** — programa
  `python -m ethos_api.account.purge_job` a diario (cron job de Render, o
  GitHub Actions con `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`). Sin él,
  las cuentas vencidas no se purgan (el deshacer funciona igual).
- [ ] **Monitores de `/mcp`** — `/mcp` ya no responde anónimo (D56); si
  tenías algún monitor apuntándole, muévelo a `/health`.

### Opcionales

- [ ] **SMTP para avisos (D52/D53)** — `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
  `SMTP_PASSWORD`, `FEEDBACK_FROM` y `FEEDBACK_TO` en Render para recibir un
  correo por sugerencia y el aviso de borrado de cuenta. Sin ellas todo se
  guarda igual en Supabase (las sugerencias, en la tabla `feedback`).
- [ ] **Plantillas de correo con el estilo de Ethos** — en Supabase →
  Authentication → Emails, pega el HTML de
  `supabase/templates/confirm-signup.html` en "Confirm signup" (asunto:
  "Confirma tu correo · Ethos") y el de
  `supabase/templates/reset-password.html` en "Reset password" (asunto:
  "Elige una nueva contraseña · Ethos"); envía uno de prueba.
- [ ] **Docker / Cloud Run (D58)** — la build de la imagen sigue sin
  verificar (2026-07-07: el daemon de Docker seguía apagado y `api/.env` no
  existe para el `--env-file`): `cd api && docker build -t ethos-api .`,
  `docker run --rm -p 8080:8080 --env-file .env ethos-api` y
  `curl http://localhost:8080/health`. Migrar a Cloud Run solo si los cold
  starts de Render molestan de verdad (requiere tarjeta con tope de gasto).

## Para ir revisando — pruebas y decisiones

### Pruebas end-to-end por categoría

- [ ] **Juegos / Steam (Fase 1)** — conecta Steam desde Fuentes, espera el
  refresco y revisa Inicio y el Detalle de Juegos con tus datos; en Conectar
  IA genera el token y prueba `games.summary` desde un cliente MCP; descarga
  `games.context.json`.
- [ ] **Música / ListenBrainz (Fase 2)** — conecta tu usuario público de
  ListenBrainz y revisa escuchas, top artistas y top canciones (últimos 30
  días); comprueba que Inicio muestra la fila activa y Fuentes la lista en
  "Activas"; prueba `music.top_artists` por MCP y descarga
  `music.context.json`.
- [ ] **Cine y TV / Trakt (Fase 3)** — necesita `TRAKT_CLIENT_ID` (ver
  Bloqueantes): conecta tu usuario, revisa horas, tops y vistos recientes;
  prueba `film.top_movies` por MCP y descarga `film.context.json`.
- [ ] **Anime y manga / AniList (Fase 3)** — sin keys ni OAuth: escribe tu
  usuario de AniList (listas públicas) y revisa episodios, nota media, mejor
  puntuados y en curso; prueba `anime.top_rated` por MCP y descarga
  `anime.context.json`.
- [ ] **Libros / Goodreads (Fase 3)** — exporta tu biblioteca (My Books →
  Import and export → Export Library), súbela en el Detalle de Libros y
  revisa leídos, páginas, leyendo ahora y autores; prueba
  `books.currently_reading` por MCP y descarga `books.context.json`. Un
  archivo que no sea el export debe rechazarse con guía (422).

### Flujos de Fase 4

- [ ] **Aviso de categorías en desarrollo (D50)** — en la landing (bloque
  "En camino") y en el panel (`/app/categoria/places`, panorama y Fuentes),
  deja un correo en "Avísame" y confirma que responde "Te avisaremos en …".
- [ ] **Entradas a mano (D51)** — en el detalle de una categoría conectada,
  abre "Añadido a mano", crea un registro, comprueba que aparece y que el
  resumen lo cuenta; bórralo y confirma que desaparece.
- [ ] **Sugerencias (D52)** — envía una sugerencia desde Ayuda y comprueba
  que llega a la tabla `feedback` (y al correo si configuraste el SMTP).
- [ ] **Borrado de cuenta (D53)** — en Ajustes: "Eliminar datos" limpia las
  fuentes; "Eliminar cuenta" muestra el banner con la fecha y "Deshacer" lo
  cancela. El correo de aviso usa el SMTP opcional.
- [ ] **OAuth del MCP (D56)** — añade el MCP de Ethos a un cliente
  compatible (p. ej. Claude) SIN token: debe recibir el 401, descubrir el
  authorization server, registrarse solo y abrirte `/oauth/autorizar` para
  aprobar. El token legacy `eth_live_` de Conectar IA sigue funcionando en
  paralelo.

### Verificación visual en producción

- [ ] **Auth** — `/auth`: alternar login/registro, mostrar/ocultar
  contraseña, validaciones (correo, mínimo 8), spinner girando al enviar;
  `/auth/recuperar` y `/auth/nueva-clave`. Ya no hay toggle de tema aquí
  (se cambia en Ajustes).
- [ ] **Shell de la app** — `/app`: barra lateral (Inicio · Fuentes ·
  Conectar IA · Ayuda), resaltado del activo, badge en "Conectar IA",
  engrane → Ajustes, header por pantalla y el responsivo (barra → top bar
  en pantallas estrechas).
- [ ] **Inicio** — banner de IA, stat band "El gusto en números", panorama
  con las cinco filas (activas o apagadas) y actividad reciente.
- [ ] **Detalle de categoría** — `/app/categoria/games`: status strip, stat
  band con sparkline, Destacados/Reciente/Listas, Refrescar y el modal
  "Descargar contexto" (pestañas JSON/MCP, copiar, descargar).
- [ ] **Fuentes** — `/app/fuentes`: resumen y las cinco categorías; con
  todas activas ya no hay grupo "En desarrollo" — confirma que te cuadra
  visualmente.
- [ ] **Conectar IA** — `/app/conectar-ia`: endpoint y token reales, tres
  pasos y el playground. Ojo: el playground es demostración con datos de
  ejemplo (D54, decidido así a propósito).
- [ ] **Ayuda y Ajustes** — FAQ, envío de sugerencias real, Perfil con tu
  nombre y correo de la cuenta (edítalo y confirma que el pie de la barra
  lateral se actualiza), Apariencia cambia el tema también en la landing
  (misma pestaña/dispositivo) y Zona de peligro.
- [ ] **Pulido de UI (2026-07-07)** — spinners/badges animados (login,
  refrescar categoría, badge de Conectar IA), logo del panel lleva a la
  landing sin cerrar sesión, formulario de la landing solo con la
  sugerencia. Si el icono de la pestaña sigue viéndose viejo, es caché:
  fuerza recarga o abre en incógnito.

### SEO y metadatos (2026-07-07)

- [ ] **Imagen OG** — rediseñada el 2026-07-07 con las tipografías reales
  (preview aprobada en sesión): comparte la URL en X/WhatsApp/Discord (o usa
  opengraph.xyz) y confirma que la tarjeta 1200×630 te convence; se genera
  en build en `web/src/app/opengraph-image.tsx` (las TTF viven en
  `web/assets/og/`).
- [ ] **Cuenta de X/Twitter** — si el proyecto tiene @usuario, dilo para
  añadir `twitter:site` (quedó fuera por no inventar un handle).
- [ ] **Dominio propio** — si algún día dejas `ethos-steel.vercel.app`,
  cambia `SITE_URL` en `web/src/app/layout.tsx` (canónica, OG y JSON-LD
  salen de ahí).
- [ ] **Favicons nuevos** — revisa en producción el icono de pestaña (SVG
  con modo oscuro), el apple-touch-icon (añadir a inicio en iOS) y el
  manifest ("Añadir a pantalla de inicio" en Android).

### Decisiones delegadas y notas de alcance

- [ ] **D32** Wishlist de Steam sin títulos en v1 (solo conteo + appids por
  prioridad); la resolución de títulos queda diferida.
- [ ] **D33** Completado solo para el top 20 por horas en cada refresco
  (protege la cuota de la API key).
- [ ] **D34** `games.context.json`: resumen + top + recientes + wishlist,
  sin histórico de eventos en v1.
- [ ] **D36** Refresco con BackgroundTasks y estados de frescura; cola
  durable después. Perfil privado de Steam → estado `private`.
- [ ] **Stat band de Inicio** — "El gusto en números" sigue mostrando cifras
  de Juegos (su meta ya cuenta las fuentes activas); si quieres que mezcle
  métricas de otras categorías, dilo y lo ajustamos.
- [ ] **Entradas a mano sin proveedor** — hoy la sección "Añadido a mano"
  vive solo en el detalle conectado; añadirla a categorías sin proveedor
  queda como mejora si la quieres.
- [ ] **Aviso real de "Avísame" (D50)** — hoy solo se guarda el interés
  (correo + categoría); el correo masivo desde `category_interest` se
  define cuando exista proveedor de correo (el SMTP de D52).

## Hecho

- [x] **Correo de contacto de Ayuda** (2026-07-07) — resuelto eliminando la
  tarjeta "¿Algo más personal?": el `mailto:hola@ethos.app` era un
  placeholder sin canal real y el buzón anónimo de la misma pantalla cubre
  el contacto. Si algún día hay correo real, se reintroduce.
- [x] **Migraciones 0001–0008 aplicadas en Supabase** (confirmado
  2026-07-07). Los flujos que dependían de 0004–0008 (música, avisos,
  sugerencias, borrado de cuenta, OAuth del MCP) ya no están bloqueados
  por base de datos.
- [x] **D35** Persistencia con respaldo Supabase: la migración 0003 está
  aplicada y los stores la usan; los datos sobreviven al redeploy.
