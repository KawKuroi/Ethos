# ACTIVE_TASK — Web: Conectar IA

Fase 1 · Web. Pantalla Conectar IA del diseño (`App Ethos.dc.html`): estado del
servidor MCP, tarjeta de conexión (endpoint + token con copiar), tres pasos, y
el playground "Pruébalo" (lado natural con chat + lado técnico "Lo que pasa por
detrás": tool + args, contexto que viaja, respuesta JSON).

### 1. Contexto y Archivos Afectados

Sin backend de MCP ni sesión todavía: endpoint/token son placeholder (los reales
llegan con el middleware de auth del MCP y el endpoint por usuario) y el
playground es simulado con datos de ejemplo de Juegos (única activa; sin LLM en
v1). El estado de conexión se simula localmente (toggle).

Archivos (se crean salvo indicación):
- `web/src/components/app/connect/*` — datos, estilos, componente y test.
- `web/src/app/app/conectar-ia/page.tsx` (mod) — renderiza `<ConnectAi/>`.

### 2. Evaluación Crítica

**Veredicto: la pantalla más interactiva; simulada como pide el roadmap (sin
LLM).** Opción recomendada: endpoint/token placeholder + tres pasos + playground
con consultas de Juegos y panel técnico. Deuda anotada: endpoint/token/estado
reales y matching de consultas llegan con el backend del MCP.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [connect/data.ts]** `ENDPOINT`, `TOKEN`, `STEPS` (3) y
  `MCP_QUERIES` (consultas de ejemplo de Juegos con tool, args, ctx/full/pct,
  answer, items y response JSON).
- [x] **Paso 2: [connect/connect.module.css]** estilos: tarjeta de estado,
  conexión (endpoint/token + copiar), tres pasos, playground (dos columnas: chat
  y panel técnico), input y respuestas.
- [x] **Paso 3: [connect/connect.tsx]** ("use client") estado del servidor
  (toggle simulado), copiar endpoint/token ("copiado ✓"), tres pasos, y
  playground: elegir consulta o escribir la propia (matching simple a Juegos),
  con typing efímero → respuesta y el panel técnico (tool 200 OK, barra de
  contexto, JSON crudo). `eth-screen`.
- [x] **Paso 4: [app/app/conectar-ia/page.tsx]** renderiza `<ConnectAi/>`.
- [x] **Paso 5: [connect/connect.test.tsx]** endpoint/token visibles; elegir una
  consulta muestra la respuesta y el panel técnico (tool + JSON).

### 4. Reporte de Pruebas

**[APROBADO]** — tsc, eslint sin incidencias; vitest 31/31 (3 nuevos de
`connect`); build OK. Endpoint/token son placeholder enmascarado (sin secreto
real); playground simulado sin LLM. Sin `any` nuevos. Verificación visual: usuario.
