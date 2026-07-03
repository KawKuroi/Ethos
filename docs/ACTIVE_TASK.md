# ACTIVE_TASK — Hardening de la API (rate limiting y anti-abuso)

Tarea: proteger la API en producción contra abuso y mal uso: límite de
peticiones por IP, CORS restringido a la web, hosts confiables, límite de
tamaño de cuerpo, cabeceras de seguridad, docs interactivos apagados en
producción y throttle del cliente de Steam (cuida la cuota de la API key).

## 1. Contexto y Archivos Afectados

(Se exceden los 5 archivos: el hardening es transversal por diseño — un
middleware nuevo + config + app + cliente Steam + infra + tests.)

- `api/src/ethos_api/middleware.py` — NUEVO: middlewares ASGI puros
  (rate limit, tamaño de cuerpo, cabeceras). ASGI puro para no romper el
  streaming SSE del MCP.
- `api/src/ethos_api/config.py` — settings de orígenes, hosts y límites.
- `api/src/ethos_api/main.py` — factory `create_app()` + pila de middlewares
  + docs solo fuera de producción.
- `api/src/ethos_api/connectors/steam/client.py` — throttle (intervalo
  mínimo entre llamadas, reloj/sleep inyectables).
- `render.yaml` — `--proxy-headers` (IP real tras el proxy de Render) y env
  vars `ALLOWED_ORIGINS` / `ALLOWED_HOSTS`.
- Tests: `api/tests/test_hardening.py` (nuevo) y ampliación de
  `test_steam_client.py`.

## 2. Evaluación Crítica

**Veredicto: bueno.** Petición directa del usuario y coherente con los
requisitos de seguridad del PRD §7. El momento es el correcto: la API acaba
de quedar pública.

Opciones:
1. (Rec.) Middlewares ASGI propios en memoria + CORS/TrustedHost de
   Starlette. Cero dependencias nuevas, tipado estricto, suficiente con una
   instancia única (Render free).
2. `slowapi` para el rate limit: dependencia extra y basada en
   BaseHTTPMiddleware (riesgo con SSE del MCP).
3. Rate limit con Redis (Upstash): necesario solo con varias réplicas; hoy
   sería costo y latencia sin beneficio.

Deuda prevista: el limitador en memoria se reinicia con cada deploy y no se
comparte entre réplicas — si el backend escala horizontalmente, migrar a un
backend compartido (anotado). El límite de cuerpo por Content-Length no
frena streaming chunked malicioso más allá del corte por desconexión.

## 3. Plan de Acción Detallado

### Bloque A — Middlewares
- [x] **Paso 1: [middleware.py]** `RateLimitMiddleware` (ventana deslizante
  por IP, 429 + Retry-After, `/health` exento, poda de memoria),
  `BodySizeLimitMiddleware` (413 por Content-Length + corte de chunked),
  `SecurityHeadersMiddleware` (nosniff, frame-deny, referrer, HSTS).

### Bloque B — Configuración y app
- [x] **Paso 2: [config.py]** `allowed_origins`, `allowed_hosts`,
  `rate_limit_per_minute`, `max_body_bytes`.
- [x] **Paso 3: [main.py]** factory `create_app()`; pila (de fuera adentro):
  SecurityHeaders → TrustedHost → CORS → BodyLimit → RateLimit; docs/redoc/
  openapi apagados si `environment == "production"`.

### Bloque C — Steam y despliegue
- [x] **Paso 4: [steam/client.py]** intervalo mínimo entre llamadas
  (default 1 s) con `clock`/`sleep` inyectables.
- [x] **Paso 5: [render.yaml]** startCommand con `--proxy-headers
  --forwarded-allow-ips '*'`; env vars `ALLOWED_ORIGINS`
  (https://ethos-steel.vercel.app) y `ALLOWED_HOSTS`
  (ethos-api-s10w.onrender.com).

### Bloque D — Tests
- [x] **Paso 6: [tests/test_hardening.py]** NUEVO: 429 tras superar el
  límite con Retry-After; `/health` exento; 413 por cuerpo grande; CORS
  permite el origen de la web y niega otros; Host no confiable → 400;
  cabeceras de seguridad presentes; docs 404 en producción.
- [x] **Paso 7: [tests/connectors/test_steam_client.py]** el throttle espera
  entre llamadas consecutivas (reloj falso, sin dormir de verdad).

## 4. Reporte de Pruebas

**[APROBADO]**

- Funcional: rate limit por IP (429 + Retry-After, `/health` exento), 413
  por cuerpo grande, cabeceras de seguridad en toda respuesta, CORS solo
  para la web, TrustedHost, docs 404 en producción y disponibles en
  desarrollo, throttle del cliente de Steam. 9 tests nuevos de hardening +
  1 de throttle.
- Idioma: identificadores en inglés; comentarios y mensajes en español.
- Secretos: grep limpio (solo declaraciones `SecretStr` y comentarios).
- Stack (uv): ruff sin issues; mypy sin issues (33 archivos); pytest 41
  passed; cobertura 94.61% (umbral 85%).
- Iteraciones dentro del ciclo: RUF012 (lista mutable de clase → tupla) y
  la concatenación lista+tupla resultante, detectada por la suite.
