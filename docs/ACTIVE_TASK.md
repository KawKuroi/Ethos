# ACTIVE_TASK — Web: Ayuda y Ajustes

Fase 1 · Web. Dos pantallas del diseño (`App Ethos.dc.html`). **Ayuda**: FAQ
(acordeón) + carril de sugerencias ("Enviado ✓") y contacto. **Ajustes**: Perfil
(nombre, usuario, zona horaria, guardar), Apariencia (tema claro/oscuro/sistema,
real vía next-themes), Datos y contexto (cifras + accesos) y Zona de peligro.

### 1. Contexto y Archivos Afectados

Apariencia se cablea de verdad a `next-themes` (claro/oscuro/sistema). Perfil y
sugerencias son efímeros (persistencia y envío reales → Fase 4). Zona de peligro:
diálogo de confirmación; el borrado real es Fase 4 (correo + purga diferida), así
que confirmar avisa que llegará con el backend. Datos y contexto enlaza a Fuentes
y Conectar IA.

Archivos (se crean salvo indicación):
- `web/src/components/app/help/*` y `web/src/components/app/settings/*`.
- `web/src/app/app/ayuda/page.tsx` y `web/src/app/app/ajustes/page.tsx` (mod).

### 2. Evaluación Crítica

**Veredicto: directas; Apariencia aporta funcionalidad real (tema).** Deuda:
perfil/sugerencias/borrado sin backend (efímeros; Fase 4). Opción recomendada:
ambas pantallas fieles, con lo real cableado (tema) y lo demás como efímero
honesto.

### 3. Plan de Acción Detallado

- [x] **Paso 1: [help/data.ts]** `FAQS` (5 preguntas/respuestas del prototipo).
- [x] **Paso 2: [help/help.module.css]** estilos: cabecera, FAQ acordeón, carril
  de sugerencias y contacto.
- [x] **Paso 3: [help/help.tsx]** ("use client") FAQ con acordeón, textarea de
  sugerencia con "Enviar →/Enviado ✓" (efímero) y contacto (mailto). `eth-screen`.
- [x] **Paso 4: [app/app/ayuda/page.tsx]** renderiza `<Help/>`.
- [x] **Paso 5: [settings/settings.module.css]** estilos: tarjetas de sección,
  formularios, selector de tema, cifras y zona de peligro + diálogo.
- [x] **Paso 6: [settings/settings.tsx]** ("use client") Perfil (efímero,
  "Guardado ✓"), Apariencia (next-themes: claro/oscuro/sistema), Datos y contexto
  (cifras + enlaces a Fuentes/Conectar IA) y Zona de peligro (confirmación; aviso
  de que el borrado llega con el backend). `eth-screen`.
- [x] **Paso 7: [app/app/ajustes/page.tsx]** renderiza `<Settings/>`.
- [x] **Paso 8: [help/help.test.tsx] + [settings/settings.test.tsx]** FAQ abre/
  cierra y sugerencia confirma; Ajustes cambia el tema y abre la confirmación.

### 4. Reporte de Pruebas

**[APROBADO]** — tsc, eslint sin incidencias; vitest 35/35 (4 nuevos de `help` y
`settings`); build OK (`/app/ayuda`, `/app/ajustes`). Apariencia cambia el tema
de verdad (next-themes); perfil/sugerencias/borrado son efímeros (Fase 4).
Secretos limpio; sin `any` nuevos. Verificación visual: usuario.
