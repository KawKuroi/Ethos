# Imagen del backend (API + MCP) para despliegues por contenedor (D58).
# Render sigue usando su runtime python (render.yaml); este Dockerfile habilita
# la vía Cloud Run (u otro host de contenedores) sin cambiar código: el mismo
# uvicorn, respetando el $PORT que inyecta la plataforma.

FROM python:3.12-slim

# uv gestiona las dependencias exactamente como en desarrollo (uv.lock).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Capa de dependencias cacheable: solo se reconstruye si cambia el lock.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY README.md ./
RUN uv sync --frozen --no-dev

# Cloud Run inyecta PORT (8080 por defecto); --proxy-headers para que el rate
# limit por IP vea al cliente real detrás del proxy de la plataforma.
ENV PORT=8080
EXPOSE 8080
CMD uv run uvicorn ethos_api.main:app --host 0.0.0.0 --port ${PORT} \
    --proxy-headers --forwarded-allow-ips '*'
