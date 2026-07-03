# Por revisar — checklist para el usuario

Cosas que quedan en tus manos: configuración de infraestructura y verificación
visual en producción. efesto va añadiendo aquí lo que no puede hacer por ti.
Marca `[x]` conforme lo revises.

## Infraestructura / configuración (desbloquea funcionalidad)

- [ ] **OAuth Google y GitHub en Supabase** — habilitar ambos proveedores
  (Authentication → Providers), con client id/secret y la redirect URL
  apuntando a `https://<tu-web>/auth/callback`. Hasta hacerlo, los botones
  "Continuar con Google/GitHub" no completan el login. (Auth, D26)
- [ ] **Variables de entorno de la web** — poblar `NEXT_PUBLIC_SUPABASE_URL` y
  `NEXT_PUBLIC_SUPABASE_ANON_KEY` en Vercel (y en `web/.env.local` para
  desarrollo). Sin ellas, `/auth` lanza el error de configuración. (D26)
- [ ] **Redirects permitidos en Supabase Auth** — añadir a la allowlist de
  "Redirect URLs" tu dominio y `…/auth/callback` (incluye el flujo de
  recuperación `…/auth/callback?next=/auth/nueva-clave`). (D26)

## Verificación visual en producción

- [ ] **Auth** — `/auth`: alternar login/registro, mostrar/ocultar contraseña,
  validaciones (correo, mínimo 8, Términos), toggle de tema; `/auth/recuperar`
  y `/auth/nueva-clave`. (D26)
- [ ] **Shell de la app** — `/app`: barra lateral (Inicio · Fuentes · Conectar
  IA · Ayuda), resaltado del activo, badge pulsante en "Conectar IA", engrane →
  Ajustes, header por pantalla, y el comportamiento responsivo (barra → top bar
  en pantallas estrechas).
- [ ] **Inicio** — `/app`: banner de IA, stat band "El gusto en números",
  panorama (Juegos activa + cuatro "en desarrollo") y actividad reciente. Ojo:
  los números y la actividad son **datos de ejemplo** del prototipo hasta que
  esté el backend de Steam; confirma que te parece bien mostrarlos así de
  momento.
