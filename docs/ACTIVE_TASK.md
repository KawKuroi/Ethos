# ACTIVE_TASK — Web: pantalla Inicio ("Tu perfil")

Fase 1 · Web. Implementar el contenido de la pantalla Inicio del diseño
(`App Ethos.dc.html`) dentro del shell: banner "Tu IA aún no está conectada",
stat band "El gusto en números", "Panorama · por actividad" (categorías con su
estado) y "Actividad reciente". Juegos activa; Música, Cine y TV, Anime y manga
y Libros como "en desarrollo" (v1, D27/roadmap).

### 1. Contexto y Archivos Afectados

Estado: el shell (`/app` layout + sidebar + header) ya existe; `app/app/page.tsx`
es el placeholder de Inicio. No hay backend de datos: como en la landing, se usan
los datos de ejemplo del prototipo (constantes, a sustituir por el backend). El
diseño de Inicio (líneas ~104-217 de `App Ethos.dc.html`): banner de IA,
(alertas globales), stat band de 4 cifras, panorama de filas por categoría
(chip+inicial, nombre, proveedor·modo, barra de share, valor hero, punto de
estado) y actividad reciente en timeline. Estados de fila: activa (barra + valor
+ punto sólido), en desarrollo (punto azul pulsante) y apagada (no aplica en v1).

Valores de ejemplo (del prototipo): Juegos → hero "1.840 horas jugadas", stats
312 juegos / 1.840 horas / 47 deseados / 38% completado; actividad de Juegos
(Balatro, Tunic, Pizza Tower). Acentos por categoría de `design.md` §1.

Archivos (se crean salvo indicación):
- `web/src/components/app/overview/*` — datos, estilos, componente y test.
- `web/src/app/app/page.tsx` (mod) — renderiza `<Overview/>`.

### 2. Evaluación Crítica

**Veredicto: buena tarea, acotada al Inicio.** Encaja con el shell y con el
aterrizaje post-login. Es una pantalla de composición con datos de ejemplo,
igual que la landing (el backend los sustituye luego).

Fronteras y decisiones:
- **v1 = Juegos activa, resto en desarrollo** (D27/roadmap). El stat band y la
  actividad se basan en Juegos (única fuente con datos); las otras cuatro salen
  como "en desarrollo" en el panorama.
- **Alertas globales agregadas.** El prototipo solo agrega alertas de nivel
  warn/error; Juegos únicamente tiene una `info`, así que la sección queda vacía
  y **oculta**. Se cablea con datos reales cuando exista el backend (se deja el
  gancho de datos preparado). No se inventan alertas.
- **Navegación al detalle.** La pantalla de Detalle de categoría es otra tarea;
  las filas del panorama son informativas por ahora (sin navegación), para no
  dejar enlaces rotos. Se conectan al llegar el Detalle.

Opciones de alcance:
1. **Inicio con banner + stat band + panorama + actividad (datos de ejemplo),
   Juegos activa** — cumple el ítem sin invadir Detalle ni el backend.
   **[Recomendada]**
2. Inicio + navegación al Detalle — arrastra la tarea de Detalle.
3. Inicio con datos reales — imposible sin el backend de Steam.

Deuda técnica prevista:
- Datos de ejemplo en constantes (a sustituir por el backend); mismo patrón que
  la landing.
- Sección de alertas oculta hasta tener datos reales.
- Filas del panorama sin navegación hasta la tarea de Detalle.

### 3. Plan de Acción Detallado

Bloque A — Datos y estilos
- [x] **Paso 1: [web/src/components/app/overview/data.ts]** `OV_STATS` (4 cifras
  de Juegos), `OV_META`, `PANORAMA` (Juegos `live` + Música/Cine/Anime/Libros
  `soon`, con accent, inicial, proveedor, hero y share), `ACTIVITY` (3 entradas
  de Juegos) y `MCP_CONNECTED = false`. Tipos explícitos.
- [x] **Paso 2: [web/src/components/app/overview/overview.module.css]** estilos:
  banner de IA, stat band (grid de 4), panorama (fila live/soon con chip, barra,
  valor, punto de estado y leyenda) y actividad (timeline con pin), desde tokens;
  `prefers-reduced-motion` para el punto pulsante.

Bloque B — Composición
- [x] **Paso 3: [web/src/components/app/overview/overview.tsx]** compone las
  secciones (sub-componentes internos): banner "Tu IA aún no está conectada" con
  CTA → `/app/conectar-ia`; stat band "El gusto en números"; "Panorama · por
  actividad" con leyenda (activa / en desarrollo) y filas; "Actividad reciente"
  en timeline. Entra con `eth-screen`.
- [x] **Paso 4: [web/src/app/app/page.tsx]** (mod) renderiza `<Overview/>` (deja
  de usar el placeholder).

Bloque C — Tests
- [x] **Paso 5: [web/src/components/app/overview/overview.test.tsx]** banner
  visible (IA sin conectar), 4 cifras del stat band, panorama con Juegos activa y
  al menos una categoría "en desarrollo", y actividad con entradas.

### 4. Reporte de Pruebas

**[APROBADO]**

- `tsc --noEmit`: sin errores. `eslint`: sin warnings.
- `vitest run`: 22/22 (4 nuevos de `overview`).
- `next build`: OK; `/app` renderiza Inicio (estática).
- Idioma: identificadores en inglés, texto humano en español (D19).
- Secretos: grep sin credenciales; sin tipos `any` nuevos.
- Alertas agregadas: sección cableada por datos (`GLOBAL_ALERTS`), hoy vacía →
  oculta (Juegos solo tiene una alerta `info`, que no se agrega).
- Verificación visual real: la hace el usuario en producción.
