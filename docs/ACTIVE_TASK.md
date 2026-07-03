# ACTIVE_TASK — Landing pública según el diseño

Tarea: implementar la landing (`/`) de `Landing mockups.dc.html` (copia local
del proyecto de diseño en `D:\Programacion\Proyectos\Ethos_claude_design`):
header, hero con flujo animado apps→Ethos→IA, sección "¿Qué es un MCP?",
"Cómo se usa", walkthrough interactivo de Juegos (4 pasos en bucle), galería
de categorías con proveedores, FAQ, sugerencias y footer. Tema claro/oscuro,
reveals de scroll y reduced-motion.

## 1. Contexto y Archivos Afectados

(Se exceden los 5 archivos: una landing de 8 secciones se compone por
componentes; agruparla en un archivo sería inmantenible.)

- `web/src/app/globals.css` — keyframes de la landing, `.eth-reveal`, tokens
  `--code-*` por tema y fuente de código.
- `web/src/app/layout.tsx` — añade JetBrains Mono (`--font-code`).
- `web/src/components/logo.tsx`, `theme-toggle.tsx` — reutilizables.
- `web/src/components/landing/` — `data.ts`, `header.tsx`, `hero.tsx`,
  `mcp-section.tsx`, `steps-section.tsx`, `walkthrough.tsx` (client),
  `gallery.tsx`, `faq-section.tsx`, `suggestions.tsx` (client), `footer.tsx`.
- `web/src/app/page.tsx` + `page.module.css` — ensamblado y estilos
  hover/animación.
- `web/src/app/app/page.tsx` — placeholder mínimo para el CTA "Abrir la app".
- Tests: `page.test.tsx` (secciones), `walkthrough.test.tsx`,
  `suggestions.test.tsx`.

## 2. Evaluación Crítica

**Veredicto: bueno.** Es el primer item web visible de Fase 1 y el diseño
está cerrado; cada push se ve en producción (Vercel).

Decisiones (recomendada aplicada):
1. **Catálogo**: el prototipo de landing trae 7 categorías; D27 fija 9. Se
   implementan las 9 (Anime y manga y Juegos de mesa toman sus datos del
   prototipo de la app, misma fuente de verdad). El hub del hero dice
   "9 categorías".
2. **Estilos**: traducción directa de los inline styles del prototipo a JSX
   + CSS Modules para hover/focus/animaciones (D29). Reescribirlo todo a
   clases sería más "limpio" pero infiel y lento.
3. **CTA "Abrir la app"**: apunta a `/app` con placeholder mínimo (la shell
   real llega en su tarea). Dejarlo muerto sería peor UX.
4. GitHub del header: repo real (`KawKuroi/Ethos`) en vez del placeholder
   del prototipo.

Deuda prevista: el formulario de sugerencias no persiste aún (usa el
efímero "Enviado ✓" del design system; el envío real está en Fase 4). El
prototipo es desktop: se añade una responsividad mínima (colapso de grids)
no especificada en el diseño — revisar con el usuario si amerita diseño
móvil propio. `animation-timeline: view()` no existe en todos los
navegadores: los reveals degradan a visible-sin-animación (progresivo).

## 3. Plan de Acción Detallado

### Bloque A — Fundación de estilos
- [x] **Paso 1: [globals.css]** keyframes del prototipo (ethRise, ethFlowY/X,
  ethBlink, ethPulseDot, ethScanX, ethGrowBar, ethProgFill), `.eth-reveal`
  (`animation-timeline: view()` + reduced-motion) y tokens `--code`,
  `--code-bg/ink/dim` por tema.
- [x] **Paso 2: [layout.tsx]** JetBrains Mono vía `next/font` (`--font-code`).

### Bloque B — Componentes compartidos
- [x] **Paso 3: [components/logo.tsx]** constelación SVG (tamaños por prop).
- [x] **Paso 4: [components/theme-toggle.tsx]** client; `useTheme` de
  next-themes; iconos sol/luna del prototipo.

### Bloque C — Datos y secciones
- [x] **Paso 5: [landing/data.ts]** CATS (9), HERO_SOURCES, MCP_POINTS,
  STEPS, WSTEPS, FAQS — textos y valores del prototipo tal cual.
- [x] **Paso 6: [landing/header.tsx + footer.tsx]** logo, toggle, GitHub,
  "Abrir la app"; footer con lema.
- [x] **Paso 7: [landing/hero.tsx]** titular, CTAs, tarjeta de flujo con
  conectores animados y burbuja de la IA.
- [x] **Paso 8: [landing/mcp-section.tsx]** explicación, diagrama
  petición/respuesta animado y 3 puntos.
- [x] **Paso 9: [landing/steps-section.tsx]** 3 pasos con flechas.
- [x] **Paso 10: [landing/walkthrough.tsx]** client: rail de 4 pasos con
  autoplay 4,2 s + barra de progreso + click; 4 paneles (conexión Steam,
  normalización con scan, tarjeta de categoría, chat de la IA).
- [x] **Paso 11: [landing/gallery.tsx]** 9 tarjetas de categoría con
  proveedores y reveal escalonado.
- [x] **Paso 12: [landing/faq-section.tsx + suggestions.tsx]** FAQ 2 col;
  formulario con "Enviado ✓" efímero.

### Bloque D — Ensamblado y tests
- [x] **Paso 13: [app/page.tsx + page.module.css + app/app/page.tsx]**
  ensambla secciones; estilos hover/focus; placeholder de `/app`.
- [x] **Paso 14: [tests]** landing renderiza secciones clave (h1, MCP,
  categorías, FAQ); walkthrough cambia de paso al click; sugerencias
  muestra "Enviado ✓"; theme-toggle alterna.

### Bloque E — Docs
- [x] **Paso 15: [docs/design.md]** §4 al día con la landing real y ruta de
  la copia local del proyecto de diseño.

## 4. Reporte de Pruebas

**[APROBADO]**

- Funcional: las 8 secciones del prototipo con sus textos exactos;
  walkthrough con autoplay/click/progreso; galería con las 9 categorías
  (D27); flujo y diagramas animados; tema claro/oscuro; reveals con
  `animation-timeline` y degradación progresiva; reduced-motion.
- Idioma: identificadores en inglés, textos y comentarios en español.
- Secretos: grep limpio en todo lo nuevo.
- Stack (pnpm): eslint sin issues (una corrección: `useSyncExternalStore`
  en vez de setState-en-efecto, regla react-hooks nueva); `tsc --noEmit`
  limpio; vitest 9 passed (landing, walkthrough, sugerencias); build de
  producción estática con `/` y `/app`.
- Deuda registrada: envío real de sugerencias (Fase 4); responsividad móvil
  mínima añadida (el prototipo es desktop) — pendiente decidir si amerita
  diseño móvil propio.
