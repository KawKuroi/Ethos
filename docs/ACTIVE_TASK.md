# ACTIVE_TASK — Fundación de /web (Next.js + tokens del diseño)

Tarea: crear `/web` (Next.js App Router, pnpm) con la fundación del diseño
(D25/D29): tokens CSS de la paleta slate + acentos por categoría, tipografías
con `next/font` (Bricolage Grotesque + Hanken Grotesk), tema
claro/oscuro/sistema con `next-themes`, animaciones base con
`prefers-reduced-motion`, testing con Vitest + Testing Library y job de CI.
Cierra la mitad `/web` del item de monorepo de Fase 0.

## 1. Contexto y Archivos Afectados

- `web/` — NUEVO: scaffold Next.js (TS, App Router, src-dir, ESLint, sin Tailwind).
- `web/src/app/globals.css` — tokens del diseño (design.md §1) y animaciones.
- `web/src/app/layout.tsx` — fuentes `next/font` + ThemeProvider.
- `web/src/components/theme-provider.tsx` — next-themes (claro/oscuro/sistema).
- `.github/workflows/ci.yml` — job `web` (lint, tipos, tests, build).
- Apoyo: `web/vitest.config.ts`, test inicial, `README.md` raíz.

## 2. Evaluación Crítica

**Veredicto: bueno.** Ejecuta la fundación que Fase 1 lista primero y la parte
de código de Fase 0; el diseño está cerrado (D25), así que no hay riesgo de
rehacer tokens. Sin choques con PRD/arquitectura.

Opciones:
1. (Rec.) create-next-app sin Tailwind + tokens CSS/CSS Modules + next-themes
   + Vitest. Traducción directa del prototipo (D29).
2. Tailwind v4: contradice D29 (el prototipo habla CSS variables nativas).
3. SPA Vite: contradice D18 (Next.js decidido).

Deuda prevista: Playwright (E2E) se difiere a cuando haya pantallas reales —
instalarlo hoy añade peso sin nada que recorrer; queda Vitest como base. El
ThemeProvider usa `suppressHydrationWarning` (patrón estándar de next-themes).

## 3. Plan de Acción Detallado

### Bloque A — Scaffold
- [x] **Paso 1: [web/]** `create-next-app` (TS, App Router, src-dir, ESLint,
  sin Tailwind, alias `@/*`, pnpm).
- [x] **Paso 2: [web/package.json]** deps `next-themes`; dev-deps Vitest +
  Testing Library + jsdom; scripts `test` y `typecheck`.

### Bloque B — Fundación del diseño
- [x] **Paso 3: [web/src/app/globals.css]** tokens de design.md: paleta slate
  clara/oscura (`data-theme`), acentos por categoría, salud/alerta, radios,
  sombras, tipos; keyframes (`ethScreen`, `spin`, `pulse`) y bloque
  `prefers-reduced-motion`.
- [x] **Paso 4: [web/src/app/layout.tsx]** `next/font/google` (Bricolage
  Grotesque 500-800, Hanken Grotesk 400-800) como variables CSS; metadata
  Ethos; `lang="es"`; ThemeProvider.
- [x] **Paso 5: [web/src/components/theme-provider.tsx]** wrapper de
  next-themes (`attribute="data-theme"`, system por defecto, storageKey
  `ethos_theme_mode`).
- [x] **Paso 6: [web/src/app/page.tsx]** placeholder mínimo con tokens (se
  sustituye por la landing real en su tarea).

### Bloque C — Tests y CI
- [x] **Paso 7: [web/vitest.config.ts + web/src/app/page.test.tsx]** Vitest +
  jsdom + Testing Library; test de render y de variables de tema.
- [x] **Paso 8: [.github/workflows/ci.yml]** job `web`: pnpm frozen-lockfile,
  eslint, `tsc --noEmit`, vitest, build.

### Bloque D — Docs
- [x] **Paso 9: [README.md raíz + web/README.md]** estructura real y comandos.

## 4. Reporte de Pruebas

**[APROBADO]**

- Funcional: `/web` con Next.js 16 (App Router, src-dir, sin Tailwind),
  tokens del diseño en `globals.css` (paleta slate clara/oscura, acentos por
  categoría, salud, radios, sombras, keyframes, reduced-motion), fuentes
  `next/font` (Bricolage Grotesque + Hanken Grotesk), `next-themes`
  (claro/oscuro/sistema, storageKey `ethos_theme_mode`), placeholder con
  `.eth-screen`.
- Idioma: identificadores en inglés; comentarios y textos en español.
- Secretos: grep limpio (solo coincidencias con la palabra "tokens de diseño").
- Stack (pnpm): eslint sin issues; `tsc --noEmit` sin issues; vitest 3
  passed (con auto-cleanup y polyfill de matchMedia para next-themes); build
  de producción estático OK. CI amplía con job `web` (lint, tipos, tests,
  build) con cache de pnpm.
- Nota: dos fallos iniciales eran del setup de tests recién escrito (cleanup
  de Testing Library y matchMedia en jsdom), corregidos dentro del paso 7.
