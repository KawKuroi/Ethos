# Ethos API

Backend de Ethos: API HTTP y servidor MCP en un solo servicio (FastAPI +
FastMCP). Gestionado con [uv](https://docs.astral.sh/uv/).

## Requisitos

- Python 3.12 (uv lo instala si falta; lo fija `.python-version`).
- uv.

## Puesta en marcha

```bash
cd api
uv sync                 # crea el entorno e instala dependencias
cp ../.env.example .env  # rellenar valores locales (no se versiona)
```

## Ejecutar

```bash
uv run uvicorn ethos_api.main:app --reload
```

- API de salud: `GET http://localhost:8000/health`
- Endpoint MCP (streamable-HTTP): `http://localhost:8000/mcp/`

## Calidad

```bash
uv run ruff check .     # lint
uv run mypy             # tipos
uv run pytest           # tests
```

## Estructura

```
api/
  src/ethos_api/
    config.py       # ajustes desde el entorno
    mcp_server.py   # instancia FastMCP y sus tools
    main.py         # FastAPI: /health + monta el MCP en /mcp
  tests/            # tests de la API y del montaje del MCP
```
