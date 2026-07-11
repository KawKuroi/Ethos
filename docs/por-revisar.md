# Por revisar — checklist para el usuario

Lo que queda en tus manos, en dos bloques: **Bloqueantes** (sin esto hay
partes del producto que no funcionan) y **Para ir revisando** (verificaciones
y decisiones sin prisa). efesto añade aquí lo que no puede hacer por ti;
marca `[x]` conforme lo resuelvas y lo movemos a Hecho.

## Bloqueantes — configuración que detiene el flujo

Nada pendiente (2026-07-11): keys, env vars, auth, SMTP y el job de purga
quedaron configurados — ver Hecho. Lo que sigue son verificaciones sin
prisa.

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
- [ ] **Cine y TV / Trakt (Fase 3)** — la key ya está en Render: conecta tu
  usuario (perfil público), revisa horas, tops y vistos recientes; prueba
  `film.top_movies` por MCP y descarga `film.context.json`.
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

### Aparcado (sin plazo)

- [ ] **Docker / Cloud Run (D58)** — descartado a corto/medio plazo
  (2026-07-11); Render sigue siendo el host. Si algún día molestan los cold
  starts: verificar la build local (`cd api && docker build -t ethos-api .`,
  `docker run --rm -p 8080:8080 --env-file .env ethos-api`,
  `curl http://localhost:8080/health` — requiere el daemon de Docker
  corriendo y un `api/.env` con las env vars) y migrar con
  `gcloud run deploy` usando las mismas env vars (requiere tarjeta con tope
  de gasto).

## Hecho

- [x] **OAuth Google** (2026-07-11) — app creada en Google Cloud Console y
  proveedor habilitado; verificado contra `/auth/v1/settings`
  (`"google": true`). La prueba del botón en producción queda cubierta por
  la verificación visual de Auth.
- [x] **Job de purga de cuentas (D53)** (2026-07-11) — workflow
  `purga-cuentas.yml` en main (diario 06:00 UTC), secrets creados y primera
  ejecución manual completada en verde.
- [x] **SMTP configurado** (2026-07-11) — Gmail con contraseña de
  aplicación en Render (`SMTP_*`, `FEEDBACK_*`, puerto 587) y en Supabase
  Auth (puerto 465); plantillas de Ethos pegadas en Confirm signup y Reset
  password. Confirmado por el usuario; el aviso real se comprobará con la
  prueba de sugerencias (D52).
- [x] **`TRAKT_CLIENT_ID` en Render** (2026-07-11) — app de Trakt creada y
  key poblada; confirmado por el usuario.
- [x] **Env vars del blueprint en Render** (2026-07-11) — `PUBLIC_BASE_URL`,
  `WEB_BASE_URL` y compañía revisadas en el dashboard; confirmado por el
  usuario.
- [x] **URL Configuration de Supabase Auth** (2026-07-11) — Site URL =
  `https://ethos-steel.vercel.app` y Redirect URLs `/auth` y `/auth/callback`
  configuradas (captura revisada). Solo si desarrollas en local: añade
  también `http://localhost:3000/auth` y `http://localhost:3000/auth/callback`.
- [x] **Supabase en la web** (2026-07-11) — Vercel ya tenía las vars (el
  auth de producción funciona) y `web/.env.local` quedó creado con
  `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` y
  `NEXT_PUBLIC_API_URL=http://localhost:8000` para desarrollo.
- [x] **Monitores de `/mcp`** (2026-07-11) — nada que mover: el keep-alive
  de UptimeRobot apunta a `/health` desde la Fase 0.
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
