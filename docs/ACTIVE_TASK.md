# ACTIVE_TASK — Ajustes de la landing tras revisión visual del usuario

Feedback del usuario sobre la landing en producción (2026-07-03):

1. Fuentes distintas al diseño → falta el eje óptico `opsz` de Bricolage
   Grotesque en `next/font` (el prototipo carga `opsz,wght@12..96`).
2. Faltan animaciones → el bloque global de `prefers-reduced-motion` apagaba
   TODAS las animaciones (el prototipo solo apaga los reveals); con los
   efectos de Windows desactivados no se veía ninguna.
3. Quitar la animación de entrada de las tarjetas de "La misma secuencia" y
   reducir el catálogo a lo básico: fuera Lugares, Comida y Juegos de mesa
   (diferidas; se verá en el futuro). Catálogo activo: Juegos, Música, Cine
   y TV, Anime y manga, Actividad física, Libros. (Revisa D27.)
4. Logo: las líneas de la constelación no se distinguen sobre algunos fondos
   → subir grosor/opacidad del trazo.
5. Textarea "Tu sugerencia": impedir el resize.

## Plan

- [x] **[web/src/app/layout.tsx]** Bricolage con `axes: ["opsz"]`.
- [x] **[web/src/app/globals.css]** reduced-motion pasa de global a
  selectivo (`.eth-screen`, `.eth-reveal`), como el prototipo.
- [x] **[web/src/components/landing/landing.module.css]** `.galleryCard` sin
  animación de entrada; `.textarea { resize: none }`.
- [x] **[web/src/components/logo.tsx]** trazo de la constelación más visible
  (grosor 1.5, opacidad .95).
- [x] **[web/src/components/landing/data.ts]** CATS a 6 (fuera Lugares,
  Comida, Juegos de mesa).
- [x] **[api/src/ethos_api/schema.py]** enum `Category` a 6 + tests.
- [x] **[docs]** D27 revisada (6 activas + 3 diferidas), prd, architecture,
  data-model, design.md, roadmap, bitácora.
- [x] **[tests]** page.test.tsx con el catálogo de 6; suite completa verde.
