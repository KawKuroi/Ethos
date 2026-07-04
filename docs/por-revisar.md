# Por revisar — checklist para el usuario

Cosas que quedan en tus manos: configuración de infraestructura y verificación
visual en producción. efesto va añadiendo aquí lo que no puede hacer por ti.
Marca `[x]` conforme lo revises.

## Infraestructura / configuración (desbloquea funcionalidad)

- [ ] **Aplicar la migración 0003 en Supabase** (persistencia real del backend,
  D35). En el dashboard de Supabase → SQL Editor → pega el contenido de
  `supabase/migrations/0003_games_and_mcp_tokens.sql` → Run. (Igual que
  hiciste con 0001-0002 en Fase 0.) Crea `user_items` y `mcp_tokens` y amplía
  `source_state`. Sin esto, el backend sigue funcionando pero en memoria (los
  datos se pierden al redeploy).
- [ ] **Verificar env vars del API en Render** — `SUPABASE_URL` y
  `SUPABASE_SERVICE_ROLE_KEY` deben estar pobladas (quedaron de Fase 0); con
  ellas el backend usa Supabase automáticamente tras el deploy del push.
- [ ] **Poblar `NEXT_PUBLIC_API_URL` en Vercel** — apúntala a
  `https://ethos-api-s10w.onrender.com`. Sin ella, las pantallas de la app no
  pueden llamar al backend (verás errores al cargar Inicio/Fuentes/Detalle).
- [ ] **Habilitar OpenID de Steam en el flujo** — necesita la Steam Web API key
  en Render (`STEAM_API_KEY`, ya de Fase 0) y que el dominio de la web esté en
  `ALLOWED_ORIGINS` del API (CORS). Prueba: en Fuentes → Juegos → "Conectar
  Steam", vuelve, y comprueba que aparecen tu biblioteca y horas.

## Prueba end-to-end de Fase 1 (cuando estén las env vars)

- [ ] Inicia sesión, conecta Steam desde Fuentes, espera el refresco y revisa
  Inicio y el Detalle de Juegos con tus datos reales.
- [ ] En Conectar IA, genera el token, copia endpoint + token y prueba una
  consulta `games.summary` desde un cliente MCP (Claude Desktop u otro).
- [ ] Descarga `games.context.json` desde el Detalle de Juegos.

- [ ] **OAuth Google y GitHub en Supabase** — habilitar ambos proveedores
  (Authentication → Providers), con client id/secret y la redirect URL
  apuntando a `https://<tu-web>/auth/callback`. Hasta hacerlo, los botones
  "Continuar con Google/GitHub" no completan el login. (Auth, D26)
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
  validaciones (correo, mínimo 8, Términos), toggle de tema; `/auth/recuperar`
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
