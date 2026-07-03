# ACTIVE_TASK — Web: Auth (login / registro / recuperación) · D26

Fase 1 · Web. Implementar las pantallas de autenticación del diseño (Claude
Design, `Auth Ethos.dc.html`) cableadas a Supabase Auth: login y registro con
correo + contraseña, Google y GitHub, y recuperación de contraseña. (D26)

### 1. Contexto y Archivos Afectados

Estado: `/web` (Next.js 16, App Router, CSS Modules + tokens, next-themes) NO
tiene ninguna integración con Supabase todavía. La landing ya está construida;
la shell de la app es un placeholder (`app/app/page.tsx`). El diseño de auth es
un layout partido (panel de marca + formulario) con toggle segmentado
login/registro, social Google/GitHub, campos (Nombre solo en registro, Correo,
Contraseña con mostrar/ocultar y mínimo 8), checkbox de Términos en registro,
spinner de submit y toggle de tema. El prototipo es UI pura (submit hace spin,
social y "olvidaste" son noop): la lógica real la aporta esta tarea.

Fuente de verdad del diseño: `D:\Programacion\Proyectos\Ethos_claude_design\
Auth Ethos.dc.html` (resumen en `design.md` §3).

Archivos directamente implicados (se crean salvo indicación):
- `web/package.json` — deps `@supabase/supabase-js` + `@supabase/ssr`.
- `web/src/lib/supabase/*` — clientes de Supabase (browser + server).
- `web/src/components/auth/*` — panel de marca, formulario y estilos.
- `web/src/app/auth/**` — rutas: pantalla principal, recuperar, nueva clave y
  callback OAuth.
- `web/src/components/landing/{header,hero}.tsx` (mod) — "Abrir la app" → `/auth`.

### 2. Evaluación Crítica

**Veredicto: buena tarea, alineada con PRD/diseño/roadmap.** Auth es el pórtico
de la app y el diseño está cerrado. Dos fronteras a respetar:

- **Dependencia de infra (OAuth).** Google y GitHub exigen habilitar los
  proveedores en el panel de Supabase (client id/secret + redirect URLs) y
  poblar `NEXT_PUBLIC_SUPABASE_URL/ANON_KEY` en Vercel. Es trabajo de cuenta del
  usuario, como en Fase 0; el código queda listo y funciona en cuanto se
  configure. El correo+contraseña sí opera ya (Email auth quedó habilitado en
  Fase 0). Se documenta como seguimiento, no bloquea el ciclo (typecheck / lint
  / build / tests no requieren credenciales reales).
- **Frontera con "Shell de la app".** La protección de rutas, el guardado de
  sesión global y el redireccionamiento fino pertenecen a la tarea de Shell
  (roadmap/design). Aquí: cliente con sesión por cookies (listo para la Shell),
  y tras login/registro correcto se redirige a `/app`.

Opciones de alcance:
1. **UI + Supabase (correo + OAuth + recuperación), sesión mínima** — cumple el
   ítem del roadmap y es verificable en CI. **[Recomendada]**
2. Solo UI (espejo del prototipo, sin Supabase) — infra-entrega: el roadmap pide
   los proveedores; habría que rehacerlo.
3. Auth completo con middleware de rutas protegidas y sesión global — se solapa
   con "Shell de la app" y no es testeable sin la config de OAuth.

Deuda técnica prevista (concreta):
- OAuth Google/GitHub inoperante hasta configurar proveedores en Supabase
  (seguimiento anotado en `current.md`).
- Guardado/expiración de sesión y guardas de ruta diferidos a la Shell.
- Se reutiliza `next-themes` (`ThemeToggle` existente) para el toggle de auth en
  vez del `ethos_theme` separado del prototipo, por consistencia con la web ya
  construida.
- Sin `packages/` de tipos compartidos aún; el cliente lee env vía
  `process.env.NEXT_PUBLIC_*`.

### 3. Plan de Acción Detallado

Bloque A — Dependencias y clientes de Supabase
- [x] **Paso 1: [web/package.json]** añadir dependencias `@supabase/supabase-js`
  y `@supabase/ssr`.
- [x] **Paso 2: [web/.env.example]** nuevo archivo con `NEXT_PUBLIC_SUPABASE_URL`
  y `NEXT_PUBLIC_SUPABASE_ANON_KEY` (documentados, sin valores).
- [x] **Paso 3: [web/src/lib/supabase/client.ts]** `getBrowserClient()` con
  `createBrowserClient` de `@supabase/ssr`, instanciado de forma perezosa (solo
  dentro de handlers) para no romper el build sin env.
- [x] **Paso 4: [web/src/lib/supabase/server.ts]** `getServerClient()` con
  `createServerClient` y el store de cookies (para el callback OAuth).

Bloque B — Pantallas de auth (fieles al diseño)
- [x] **Paso 5: [web/src/components/auth/auth.module.css]** estilos del layout
  partido, panel de marca (sparks flotantes), campos, social, divisor, checkbox,
  submit y spinner, desde los tokens; con `prefers-reduced-motion`.
- [x] **Paso 6: [web/src/components/auth/brand-panel.tsx]** panel de marca
  estático (wordmark, "Tu gusto, hecho contexto.", 3 perks, nota de privacidad).
- [x] **Paso 7: [web/src/components/auth/auth-form.tsx]** ("use client")
  formulario segmentado login/registro: estado de modo, campos, mostrar/ocultar
  contraseña, checkbox de Términos (obligatorio en registro), validación de
  correo y mínimo 8, spinner, mensajes de error en español. Acciones:
  `signInWithPassword`, `signUp`, `signInWithOAuth({provider})` con
  `redirectTo` al callback; enlace "¿Olvidaste tu contraseña?" → `/auth/recuperar`.
- [x] **Paso 8: [web/src/app/auth/page.tsx]** compone `BrandPanel` + `AuthForm`
  + `ThemeToggle`.
- [x] **Paso 9: [web/src/app/auth/recuperar/page.tsx]** solicitar restablecimiento
  (correo → `resetPasswordForEmail` con `redirectTo` a `/auth/nueva-clave`),
  con estado "Enviado ✓".
- [x] **Paso 10: [web/src/app/auth/nueva-clave/page.tsx]** fijar nueva contraseña
  (`updateUser({password})`) tras el enlace del correo.
- [x] **Paso 11: [web/src/app/auth/callback/route.ts]** intercambia el código por
  sesión (`exchangeCodeForSession`) y redirige a `/app`; a `/auth` con error si
  falla.

Bloque C — Entrada desde la landing
- [x] **Paso 12: [web/src/components/landing/{header,hero}.tsx]** "Abrir la app"
  apunta a `/auth`.

Bloque D — Tests
- [x] **Paso 13: [web/src/components/auth/auth-form.test.tsx]** con el cliente de
  Supabase mockeado: render, alternar login/registro, validación (mínimo 8,
  Términos), mostrar/ocultar contraseña y que el submit llama al método correcto.

### 4. Reporte de Pruebas

**[APROBADO]**

- `tsc --noEmit`: sin errores.
- `eslint`: sin warnings.
- `vitest run`: 15/15 (6 nuevos de `auth-form`; ajustado `page.test.tsx` porque
  los CTA de la landing pasan de `/app` a `/auth`).
- `next build`: OK; rutas `/auth`, `/auth/recuperar`, `/auth/nueva-clave`
  (estáticas) y `/auth/callback` (dinámica) generadas.
- Idioma: identificadores en inglés, texto humano en español (convención D19).
- Secretos: grep sin credenciales hardcodeadas; solo `.env.example` con claves
  vacías. Sin tipos `any` nuevos.
- Verificación visual real: la hace el usuario en producción (OAuth requiere
  habilitar Google/GitHub en Supabase).
