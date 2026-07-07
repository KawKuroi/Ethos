# Ethos

App web que reúne tu historial de tracking (música, cine/TV, libros, juegos), lo
normaliza y lo entrega a una IA vía un servidor MCP y a ti como panel de
estadísticas. Monorepo hospedado, objetivo 0 USD/mes.

## Estructura

```
/api        backend Python (FastAPI + FastMCP): API y servidor MCP
/web        app Next.js (App Router); implementa el diseño (docs/design.md)
/supabase   migraciones SQL, esquema y RLS
/docs       documentación de contexto
```

## Backend

Requiere [uv](https://docs.astral.sh/uv/). Detalle en [api/README.md](api/README.md).

```bash
cd api
uv sync
uv run uvicorn ethos_api.main:app --reload   # expone /health y /mcp/
```

Imagen de contenedor (vía Cloud Run u otro host): `docker build -t ethos-api api/`.

## Web

Requiere Node 24 y pnpm. Detalle en [web/README.md](web/README.md).

```bash
cd web
pnpm install
pnpm dev   # http://localhost:3000
```

## Documentación

Contexto, arquitectura, modelo de datos y roadmap en [docs/](docs/).
