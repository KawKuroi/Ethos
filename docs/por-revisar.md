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
- [ ] **Redirects permitidos en Supabase Auth** — en URL Configuration: Site
  URL = `https://<tu-web>` (hoy está en localhost: por eso la confirmación
  te llevó a `http://localhost:3000/?code=…`) y añade a "Redirect URLs"
  `https://<tu-web>/auth` (retorno de la confirmación de correo, va al login)
  y `https://<tu-web>/auth/callback` (OAuth y recuperación); en desarrollo,
  las mismas con `http://localhost:3000`. (D26)
- [ ] **Plantillas de correo con el estilo de Ethos** — en Supabase →
  Authentication → Emails, pega el HTML de
  `supabase/templates/confirm-signup.html` en "Confirm signup" (asunto
  sugerido: "Confirma tu correo · Ethos") y el de
  `supabase/templates/reset-password.html` en "Reset password" (asunto:
  "Elige una nueva contraseña · Ethos"). Envía uno de prueba y revisa cómo
  se ve.

## Fase 4 · Aviso de categorías en desarrollo (D50)

- [ ] **Aplicar la migración 0005** (`category_interest`) en Supabase antes de
  usar el aviso en producción; sin ella, `POST /category-interest` falla al
  persistir.
- [ ] **Mecanismo de aviso real pendiente**: hoy solo se guarda el interés
  (correo + categoría). Falta decidir cómo avisar cuando una categoría diferida
  se active (correo masivo desde la lista `category_interest`) — se define
  cuando exista proveedor de correo (ver tarea de sugerencias/contacto).
- [ ] **Verifica el flujo**: en la landing (bloque "En camino") y en el panel
  (`/app/categoria/places`, panorama y Fuentes), deja un correo en "Avísame" y
  confirma que responde "Te avisaremos en …".

## Fase 4 · Entradas a mano (D51)

- [ ] **Verifica el flujo**: en el detalle de una categoría conectada (p. ej.
  Libros), abre "Añadido a mano", crea un registro y comprueba que aparece y
  que el resumen lo cuenta; bórralo y confirma que desaparece.
- [ ] Nota de alcance: por ahora la sección "Añadido a mano" vive en el detalle
  **conectado**. Añadirla también a categorías sin proveedor conectado (para
  llevar solo entradas a mano) queda como mejora si la quieres.

## Fase 4 · Sugerencias y contacto (D52)

- [ ] **Aplicar la migración 0006** (`feedback`) en Supabase antes de recibir
  sugerencias en producción.
- [ ] **Configurar el aviso por correo (opcional)**: pon `SMTP_HOST`,
  `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FEEDBACK_FROM` y `FEEDBACK_TO` en
  Render para recibir un correo por cada sugerencia. Sin ellas, las sugerencias
  se guardan igual en la tabla `feedback` (las revisas en Supabase).
- [ ] **Dirección de contacto real**: el botón "Escribir" de Ayuda usa
  `mailto:hola@ethos.app` (placeholder). Cámbialo por tu correo real en
  `web/src/components/app/help/help.tsx`.

## Fase 4 · Borrado de cuenta (D53)

- [ ] **Aplicar la migración 0007** (`account_deletions`) en Supabase.
- [ ] **Programar el job de purga**: ejecuta `python -m ethos_api.account.purge_job`
  a diario (cron job de Render, o GitHub Actions con las env vars
  `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`). Sin él, las cuentas vencidas
  no se purgan (el deshacer funciona igual).
- [ ] **Verifica el flujo** en Ajustes: "Eliminar datos" limpia las fuentes;
  "Eliminar cuenta" muestra el banner con la fecha y "Deshacer" lo cancela.
  El correo de aviso usa el mismo SMTP opcional de sugerencias (D52).

## Fase 4 · OAuth 2.1 del MCP (D56)

- [ ] **Aplicar la migración 0008** (`oauth_clients` + `oauth_tokens`) en Supabase.
- [ ] **Poblar en Render** `PUBLIC_BASE_URL` (URL pública del API, p. ej.
  `https://ethos-api-s10w.onrender.com`) y `WEB_BASE_URL` (p. ej.
  `https://ethos-steel.vercel.app`): son el issuer OAuth y la página de
  consentimiento. Sin ellas se derivan de la petición (vale en local).
- [ ] **Verifica el flujo**: añade el MCP de Ethos a un cliente compatible
  (p. ej. Claude) SIN token; debe recibir el 401, descubrir el authorization
  server, registrarse solo y abrirte `/oauth/autorizar` para aprobar. El token
  legacy `eth_live_` de Conectar IA sigue funcionando en paralelo.
- [ ] **Ojo**: `/mcp` ya no responde anónimo (antes el tool `ping` era
  público); si tenías algún monitor apuntando a `/mcp`, muévelo a `/health`.

## Fase 4 · Dockerfile / Cloud Run (D58) y blueprint de Render

- [ ] **Verificar la build de la imagen** (el daemon de Docker no estaba
  corriendo en la máquina al crearla): `cd api && docker build -t ethos-api .`
  y luego `docker run --rm -p 8080:8080 --env-file .env ethos-api` +
  `curl http://localhost:8080/health`.
- [ ] **Render**: el blueprint ahora declara `PUBLIC_BASE_URL`, `WEB_BASE_URL`,
  `TRAKT_CLIENT_ID` y las SMTP opcionales — puebla en el dashboard las que
  falten (los blueprints existentes no añaden env vars solos).
- [ ] Migrar a Cloud Run solo si los cold starts molestan de verdad: requiere
  tarjeta (con tope de gasto). Guía: build de la imagen → `gcloud run deploy`
  con las mismas env vars.

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
