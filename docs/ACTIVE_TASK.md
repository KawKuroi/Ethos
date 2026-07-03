# ACTIVE_TASK — Web: Shell de la app (navegación lateral + header + badge)

Fase 1 · Web. Implementar el armazón de la app del diseño (Claude Design,
`App Ethos.dc.html`): barra lateral con navegación (Inicio · Fuentes · Conectar
IA · Ayuda + Ajustes), header con título/subtítulo por pantalla y el badge
pulsante en "Conectar IA" mientras la IA no esté conectada. Las pantallas
concretas (Inicio, Detalle, Fuentes, etc.) son tareas aparte del roadmap: aquí
se dejan como placeholders dentro del shell.

### 1. Contexto y Archivos Afectados

Estado: `/web` con la landing y la auth ya construidas. `app/app/page.tsx` es un
placeholder de pantalla completa; tras el login la auth redirige a `/app`. El
diseño (`App Ethos.dc.html`, resumen en `design.md` §2) define un `<aside>` de
250px (logo, nav con iconos, footer de perfil + engrane) y un `<main>` con header
sticky (título + subtítulo). El badge es un punto ámbar pulsante (`animation:
pulse`) junto a "Conectar IA" cuando `mcpConnected` es falso. Los títulos por
pantalla del diseño: Inicio "Tu perfil / El gusto, reunido y normalizado",
Fuentes, Conectar IA, Ayuda y Ajustes (líneas del diseño).

Rutas en español para segmentos de cara al usuario, como en la auth ya publicada
(`/auth/recuperar`, `/auth/nueva-clave`): `/app`, `/app/fuentes`,
`/app/conectar-ia`, `/app/ayuda`, `/app/ajustes`.

Archivos directamente implicados (se crean salvo indicación):
- `web/src/components/app/*` — datos de navegación, estilos, sidebar, header y
  placeholder de pantalla.
- `web/src/app/app/layout.tsx` — layout con el shell.
- `web/src/app/app/page.tsx` (mod) + `fuentes|conectar-ia|ayuda|ajustes/page.tsx`
  — pantallas como placeholders dentro del shell.

### 2. Evaluación Crítica

**Veredicto: buena tarea, directa y bien acotada.** El shell es un layout
compartido de Next (App Router): un `layout.tsx` bajo `/app` que envuelve las
rutas de pantalla. Encaja con el diseño y con la redirección post-login que
quedó apuntando a `/app`.

Fronteras y decisiones:
- **Contenido de pantallas fuera de alcance.** Inicio, Detalle, Fuentes, Conectar
  IA, Ayuda y Ajustes son ítems propios del roadmap; aquí van como placeholders.
  Las acciones del header dependientes de pantalla (p. ej. "Refrescar todo" en
  Fuentes) llegan con cada pantalla.
- **Estado de conexión del MCP.** No hay backend de sesión MCP todavía: el badge
  usa `mcpConnected = false` fijo (placeholder), de modo que el badge se ve. Se
  sustituirá por estado real en la tarea de Conectar IA.
- **Resaltado activo** por `usePathname` (sidebar y header como client
  components); el resto del shell es estático.

Opciones de alcance:
1. **Shell (layout + nav + header + badge) con placeholders por pantalla** —
   cumple el ítem del roadmap sin invadir las pantallas. **[Recomendada]**
2. Shell + contenido de Inicio — mezcla dos ítems del roadmap.
3. Solo la barra lateral, sin rutas por pantalla — deja la navegación sin destino.

Deuda técnica prevista (concreta):
- Badge con estado fijo hasta que exista la conexión MCP real.
- Responsividad mínima (la barra pasa a top bar en pantallas estrechas); el
  diseño fino móvil se pulirá en Fase 4.
- Sin guardas de ruta aún (sesión): diferido a integrarse cuando la Shell y el
  auth se junten; hoy `/app` es accesible directo (igual que el placeholder
  previo).

### 3. Plan de Acción Detallado

Bloque A — Datos y layout del shell
- [x] **Paso 1: [web/src/components/app/nav.ts]** `NAV` (id, label, href, clave de
  icono) para Inicio/Fuentes/Conectar IA/Ayuda y `SCREEN_META` (href →
  {title, sub}) con los textos del diseño, incluida la ruta de Ajustes.
- [x] **Paso 2: [web/src/components/app/app.module.css]** estilos del shell: aside
  250px, logo, nav con estado activo y hover, badge pulsante, footer de perfil,
  header sticky, contenedor de main; responsivo (aside → top bar en <820px) y
  `prefers-reduced-motion`.
- [x] **Paso 3: [web/src/components/app/nav-icons.tsx]** iconos SVG inline del
  diseño (grid, nodos, estrella, ayuda, engrane) por clave.
- [x] **Paso 4: [web/src/components/app/sidebar.tsx]** ("use client") logo +
  wordmark, nav con resaltado por `usePathname`, badge en "Conectar IA" cuando
  `mcpConnected` es falso, footer "Tu perfil / @tu_gusto" + engrane → `/app/ajustes`.
- [x] **Paso 5: [web/src/components/app/app-header.tsx]** ("use client") título +
  subtítulo según `usePathname` desde `SCREEN_META`.
- [x] **Paso 6: [web/src/app/app/layout.tsx]** compone `Sidebar` + `main`
  (`AppHeader` + contenedor + `children`).

Bloque B — Pantallas como placeholders dentro del shell
- [x] **Paso 7: [web/src/components/app/screen-placeholder.tsx]** placeholder
  reutilizable ("en construcción") con `eth-screen`, que recibe el nombre.
- [x] **Paso 8: [web/src/app/app/page.tsx]** (mod) Inicio usa el placeholder
  dentro del shell (deja de ser pantalla completa).
- [x] **Paso 9: [web/src/app/app/fuentes/page.tsx]** placeholder.
- [x] **Paso 10: [web/src/app/app/conectar-ia/page.tsx]** placeholder.
- [x] **Paso 11: [web/src/app/app/ayuda/page.tsx]** placeholder.
- [x] **Paso 12: [web/src/app/app/ajustes/page.tsx]** placeholder.

Bloque C — Tests
- [x] **Paso 13: [web/src/components/app/sidebar.test.tsx]** con `usePathname`
  mockeado: render de los 4 destinos, resaltado del activo y badge visible en
  "Conectar IA".

### 4. Reporte de Pruebas

**[APROBADO]**

- `tsc --noEmit`: sin errores.
- `eslint`: sin warnings.
- `vitest run`: 18/18 (3 nuevos de `sidebar`).
- `next build`: OK; rutas `/app`, `/app/fuentes`, `/app/conectar-ia`,
  `/app/ayuda`, `/app/ajustes` (estáticas) generadas bajo el layout del shell.
- Idioma: identificadores en inglés, texto humano en español (D19).
- Secretos: grep sin credenciales; sin tipos `any` nuevos.
- Verificación visual real: la hace el usuario en producción.
