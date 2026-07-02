# Ethos Web

App Next.js (App Router) de Ethos. Implementa el diseño de Claude Design
(`docs/design.md`, D25): tokens CSS de la paleta slate, tipografías Bricolage
Grotesque + Hanken Grotesk (`next/font`), tema claro/oscuro/sistema
(`next-themes`) y gráficos SVG propios (D29). Gestionada con pnpm.

## Puesta en marcha

```bash
cd web
pnpm install
pnpm dev        # http://localhost:3000
```

## Calidad

```bash
pnpm lint        # eslint
pnpm typecheck   # tsc --noEmit
pnpm test        # vitest (jsdom + Testing Library)
pnpm build       # build de producción
```

## Estructura

```
web/
  src/app/          rutas (App Router); globals.css lleva los tokens del diseño
  src/components/   componentes compartidos (theme-provider, ...)
  vitest.config.ts  tests unitarios/componentes
```
