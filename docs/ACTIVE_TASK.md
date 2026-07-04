# ACTIVE_TASK — Cableado web ↔ API (cierre de Fase 1)

Fase 1. Conectar las pantallas de la web al backend real con la sesión de
Supabase, sustituyendo los datos de ejemplo de Juegos por datos del usuario.
Las categorías "en desarrollo" siguen con constantes (no tienen backend).

### 1. Contexto y Archivos Afectados

La web tiene auth con sesión en cookies (`@supabase/ssr`). El API expone
`/sources/games`, `/context/games`, `/sources/steam[/refresh]`, `/mcp-token`
y las tools MCP, autenticados con el JWT de Supabase. Falta: un cliente de API
en la web que adjunte el token, y que Inicio/Fuentes/Detalle/Conectar IA lean
datos reales; más el flujo de conexión de Steam por OpenID (redirect + retorno).

Afectados — **API**: `games/router.py` (resumen en `/sources/games` + endpoint
de login de Steam) y sus tests. **Web**: `lib/api.ts` (nuevo), `.env.example`,
`overview/`, `sources/`, `category/`, `connect/`, ruta de retorno de Steam y
tests.

### 2. Evaluación Crítica — decisiones tomadas

- **Fetch en cliente**: las pantallas con datos por usuario pasan a client
  components que piden al API con el `access_token` de la sesión del navegador
  (estados loading / vacío / error). Evita duplicar la sesión en el server de
  Next y reutiliza el cliente ya montado.
- **`/sources/games` devuelve el resumen** (`GamesSummary | null`) además del
  estado: una sola llamada alimenta Fuentes, Inicio y Detalle. Se actualizan sus
  tests (cambia la forma).
- **Sin sparkline con datos reales**: no hay serie temporal en v1 (D34); el
  Detalle omite el sparkline hasta que lleguen los eventos (Fase 2).
- **Conexión de Steam**: `GET /sources/steam/login?return_to=` devuelve la URL
  de OpenID; la web redirige, Steam vuelve a `/app/steam/return`, esa página
  postea los `openid.*` a `/sources/steam` y encola el refresco.
- **Estados de categoría reales**: Juegos sin conectar aparece **apagada** (con
  CTA Conectar Steam), no "activa"; `private` guía a hacer público el perfil.
- **Conectar IA**: endpoint y token reales de `/mcp-token`; el playground sigue
  simulado (D-decisión previa).
- Nuevo env `NEXT_PUBLIC_API_URL` (a poblar en Vercel; anotado en por-revisar).

### 3. Plan de Acción Detallado

Bloque A — API
- [x] **Paso 1: [games/router.py]** `SourceStatusOut` con `summary`; construir
  el resumen en `GET /sources/games`. `GET /sources/steam/login` → URL OpenID.
- [x] **Paso 2: [tests/games/test_games_api.py]** ajustar a la nueva forma y
  añadir test del login.

Bloque B — Web · infraestructura
- [x] **Paso 3: [web/.env.example]** `NEXT_PUBLIC_API_URL`.
- [x] **Paso 4: [web/src/lib/api.ts]** `apiFetch` con Bearer de la sesión +
  helpers tipados (`getGamesSource`, `getMcpToken`, `steamLoginUrl`,
  `connectSteam`, `refreshSteam`, `downloadGamesContext`).
- [x] **Paso 5: [web/src/components/app/connect-steam.tsx]** botón que pide la
  URL y redirige; **[web/src/app/steam/return/page.tsx]** retorno que postea.

Bloque C — Web · pantallas
- [x] **Paso 6: [sources]** Juegos desde el estado real (activa/apagada/private
  con CTA); las demás, constantes.
- [x] **Paso 7: [overview]** stat band, panorama de Juegos y actividad desde el
  resumen; estado vacío cuando no hay datos.
- [x] **Paso 8: [category]** Detalle de Juegos con datos reales (status strip,
  stat band, top, reciente), refrescar y descargar reales; estados apagada/
  private; las soon quedan igual.
- [x] **Paso 9: [connect]** endpoint y token reales de `/mcp-token`.

Bloque D — Tests
- [x] **Paso 10: [web tests]** mockear `lib/api`; actualizar overview/sources/
  category/connect y cubrir el cliente y el retorno de Steam.

### 4. Reporte de Pruebas

**[APROBADO]**

- API: ruff, mypy, pytest 86/86. Web: tsc, eslint, vitest 38/38, next build OK
  (rutas /app/* y /steam/return generadas).
- Cableado: Inicio, Fuentes y Detalle de Juegos leen de `/sources/games`;
  descarga desde `/context/games`; Conectar IA construye el endpoint y genera
  el token desde `/mcp-token`; conexión de Steam por OpenID (login + retorno).
- Estados reales: Juegos apagada→CTA Conectar Steam, private→guía, fresh→datos.
  Las categorías en desarrollo siguen con constantes (sin backend).
- Secretos: el token de sesión viaja solo en Authorization; grep limpio.
- Pendiente del usuario: poblar `NEXT_PUBLIC_API_URL` en Vercel (por-revisar).
  Verificación end-to-end real: la hace el usuario en producción.
