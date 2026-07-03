# Diseño de la interfaz — Contexto

La fuente de verdad de la UI es el diseño hecho en Claude Design: proyecto
"Prototipo creativo de aplicación" (`c3e4858c-944b-427a-b1b7-6c327a8a1dd1`,
https://claude.ai/design/p/c3e4858c-944b-427a-b1b7-6c327a8a1dd1). Fidelidad
alta: colores, tipografía, espaciado, textos e interacciones son finales.
Ante cualquier duda de implementación manda el prototipo, no este resumen.

Copia local completa del proyecto de diseño:
`D:\Programacion\Proyectos\Ethos_claude_design` (misma estructura que el
proyecto remoto; usarla como fuente al implementar).

Archivos del proyecto de diseño:

| Archivo | Contenido |
|---------|-----------|
| `App Ethos.dc.html` | App completa (fuente editable del prototipo) |
| `Auth Ethos.dc.html` | Login / registro |
| `Landing mockups.dc.html` | Landing pública |
| `claude_code_handoff/ethos-app.html` | Bundle autocontenido de la app (abre en navegador) |
| `claude_code_handoff/ethos-landing.html` | Bundle autocontenido de la landing |
| `claude_code_handoff/README.md` | Handoff: tokens, pantallas, interacciones |

## 1. Tokens

- Tipografías (fijas, sin selector): Bricolage Grotesque (display, 700–800)
  y Hanken Grotesk (texto/UI y datos, 400–700).
- Paleta única "slate", tema claro / oscuro:
  paper `#eff1f3`/`#141619` · surface `#ffffff`/`#1d2024` · soft `#e5e8ec`/`#25282d`
  · ink `#1b1e23`/`#eef0f3` · muted `#828791`/`#888d97` · line `#dce0e5`/`#2d3036`
  · accent `#394150`/`#c3c8d2` · on-accent `#ffffff`/`#141619`.
- Acentos por categoría (landing y app): Juegos `#3b82c4` · Música `#d8543f`
  · Cine y TV `#8b5cf6` · Anime y manga `#e0883c` · Actividad física `#c64b78`
  · Libros `#2f9e6b` · Lugares `#6f8f3f` · Comida `#b07b3e` · Juegos de mesa
  `#3f8f8f`. (El prototipo trae además Pódcasts `#5b6ee0` y YouTube `#d15b5b`,
  fuera del catálogo del producto por D27.)
- Salud/alerta: ok `#3aa06a` · warn `#d99a2b` · error `#d9483b`.
- Radios: card 14px (10px en app), pill 999px. Sombras suaves; hover eleva.
- Logo: constelación SVG inline (sin imágenes externas).

## 2. Pantallas de la app

Navegación lateral: Inicio · Fuentes · Conectar IA · Ayuda (+ Ajustes por
icono). Badge pulsante en "Conectar IA" mientras la IA no esté conectada.

- **Inicio** ("Tu perfil"): banner "Tu IA aún no está conectada" (mismo diseño
  que la tarjeta de Conectar IA); alertas globales agregadas ("Necesitan tu
  atención", colapsable, muestra 3 y "Ver N más"); stat band "El gusto en
  números" (4 cifras); "Panorama · por actividad": todas las categorías como
  filas con inicial, share %, barra, sparkline y estado (activa / apagada /
  en desarrollo, con CTA "Conectar →"); "Actividad reciente" en timeline.
- **Detalle de categoría**: header con Refrescar y Descargar contexto; status
  strip único e interactivo (salud · Proveedor con "cambiar" · toggle
  API/Import · última actualización); stat band destacado (hero + sparkline +
  grid de 4 stats); secciones Destacados / Reciente / Listas (+ Conexión solo
  en modo import); alertas por categoría con acción (Renovar / Reintentar).
  Estados: conectada; apagada (guía para conectar o subir export con
  drag&drop y pasos por proveedor); en desarrollo ("Avísame cuando esté
  lista"). Modal "Descargar contexto": preview con pestañas JSON / MCP,
  copiar, "↓ Descargar archivo" (`<categoria>.context.json`).
- **Fuentes**: resumen (activas · expuestas por MCP · apagadas · en
  desarrollo); tres grupos ordenados alfabéticamente: Activas (salud:
  Operativa / Requiere atención / Error de sync), Apagadas · sin empezar
  (CTA "Conectar fuente →" o "Subir export →"), En desarrollo · próximamente.
  Método por categoría: "API disponible" o "Solo import".
- **Conectar IA**: tarjeta "Conexión del servidor" (endpoint por usuario
  `https://…/mcp/u/<id>`, token `eth_live_…` enmascarado con copiar, nota
  "Cifrado en reposo. Nunca se reenvía a las APIs de origen"); tres pasos
  (abrir cliente MCP → pegar endpoint y token → preguntar); playground
  "Pruébalo: pregúntale a tu IA": chat con composer y consultas de ejemplo, y
  panel técnico "Lo que pasa por detrás" con (1) tool llamada y args, (2)
  contexto que viaja ("0,4 KB de 84 KB"), (3) respuesta cruda JSON.
- **Ayuda**: FAQ (5 preguntas, acordeón); formulario de sugerencias (chip de
  categoría + tipo Idea/Proveedor/Problema + texto, "Enviado ✓"); contacto
  personal ("Escríbenos").
- **Ajustes**: Perfil (nombre, handle, zona horaria); Apariencia (tema claro /
  oscuro / sistema, persistido en el dispositivo); Datos y contexto (fuentes
  activas, registros, "Gestionar fuentes →"); Zona de peligro (eliminar todos
  los datos; eliminar cuenta con correo de deshacer de 30 días).

## 3. Auth (`Auth Ethos.dc.html`)

Layout partido: panel de marca (fondo accent, wordmark, "Tu gusto, hecho
contexto.", 3 perks, "Perfil privado · tú decides qué se comparte") + panel de
formulario. Segmented Iniciar sesión / Crear cuenta; social "Continuar con
Google" y "Continuar con GitHub"; divisor "o con tu correo"; campos Nombre
(solo registro), Correo, Contraseña (mostrar/ocultar, mínimo 8, "¿Olvidaste tu
contraseña?" en login); checkbox de Términos y Política de privacidad
(registro); submit con spinner; toggle de tema.

## 4. Landing (`Landing mockups.dc.html`)

Header (logo, toggle de tema, GitHub, "Abrir la app"); hero "Reúne lo que te
gusta y / Dáselo a tu IA" con tarjeta de flujo animada (pills de apps → hub
"Ethos · tu perfil" con chip "servidor MCP" → burbuja de la IA; puntos que
fluyen por conectores punteados); sección "¿Qué es un MCP?" (`#mcp`):
explicación, diagrama Tu IA ↔ Ethos (petición `ethos.juegos`, respuesta
"124 juegos · 2,4 kB", ambas animadas) y 3 tarjetas de beneficios; "Cómo se
usa" (3 pasos con flechas); "Una categoría, de tu app hasta tu IA"
(`#categorias`): walkthrough interactivo de Juegos en 4 pasos — rail con
autoplay de 4,2 s en bucle y barra de progreso; paneles: conexión de Steam
(código GET + cursor), normalización crudo→esquema con escaneo, tarjeta de
categoría (3 stats + top 3 con barras) y chat de la IA con nota de privacidad
— más galería "La misma secuencia, para cada parte de tu gusto" (una tarjeta
por categoría con sus fuentes); FAQ (4, dos columnas); sugerencias (nombre,
correo, texto); footer "Ethos — tu gusto, ordenado.". Nota: el prototipo
lista 7 categorías; el producto implementa las 9 de D27.

## 5. Interacciones y animaciones

- Cambio de pantalla: deslizamiento sutil hacia arriba (`translateY 12→0`,
  ~0.34s, solo transform). Reveals de la landing con
  `animation-timeline: view()`. Todo se desactiva con
  `prefers-reduced-motion: reduce`.
- Tarjetas de categoría: toda la tarjeta clickable; hover eleva (-3px) +
  sombra + borde acentuado.
- Efímeros: "Copiado ✓" 1.4s · "Descargado ✓" 1.6s · "Enviado ✓" · spinner de
  refresco ~1.4s → "hace unos seg" · respuesta del playground ~0.7s.
- Cambiar proveedor: diálogo de selección por radio; al confirmar se pregunta
  "¿Qué hacemos con el histórico?" (Conservar histórico / Reemplazar).
- Tema: claro / oscuro / sistema, persistido en `localStorage`
  (`ethos_theme_mode`; la landing y auth usan `ethos_theme`).

## 6. Reglas de datos visibles en la UI

- Estados de categoría: activa (live) · apagada (off: existe sin datos) · en
  desarrollo (soon: conector no listo, no activable).
- Solo import (sin API): Comida y Juegos de mesa. El estado "en desarrollo"
  (que el prototipo ilustra con Pódcasts y YouTube, excluidas del producto por
  D27) se reutiliza para el despliegue secuencial: toda categoría del catálogo
  aún no implementada se muestra así.
- Frescura por fuente: fresh / stale / syncing, con etiqueta relativa
  ("hace 2 h", "import hace 3 sem", "sincronizando…").
- Salud por fuente: error de sync > requiere atención (warn o stale) >
  operativa.
- Alertas por categoría con nivel (info/warn/error) y acción opcional; las
  no-info se agregan en Inicio ordenadas por severidad.
- Guías de import por proveedor (dónde conseguir el export, formato y pasos):
  Goodreads, StoryGraph, Beli, Untappd, BoardGameGeek, Letterboxd, Swarm, más
  una guía genérica por defecto.
