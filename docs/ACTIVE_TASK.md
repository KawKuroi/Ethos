# ACTIVE_TASK — Backend de credenciales de usuario (sesión + cifrado + endpoints)

Tarea: implementar el sistema con que cada usuario conecta su credencial personal
de un proveedor (p. ej. ListenBrainz): autenticación de sesión (Supabase Auth
JWT), cifrado de la credencial a nivel de app, y endpoints para conectar, listar
y desconectar. La persistencia usa un repositorio abstracto con implementación en
memoria; el repositorio respaldado por Supabase queda para el siguiente ciclo.

Steam no entra aquí: usa OpenID + key del servidor (D12), no credencial por
usuario.

## 1. Contexto y Archivos Afectados

Trabajo en `/api` y una migración nueva en `/supabase`. Archivos:

- `supabase/migrations/0002_user_credentials.sql` — tabla + RLS owner-only.
- `api/pyproject.toml` — deps `cryptography` y `pyjwt`; ruff: permitir `Depends`.
- `.env.example` y `api/src/ethos_api/config.py` — `SUPABASE_JWT_SECRET`.
- `api/src/ethos_api/security.py` — `TokenCipher` (Fernet) cifra/descifra.
- `api/src/ethos_api/auth.py` — dependencia `get_current_user_id` (verifica JWT).
- `api/src/ethos_api/credentials/__init__.py`
- `api/src/ethos_api/credentials/models.py` — modelos de credencial.
- `api/src/ethos_api/credentials/repository.py` — Protocol + impl en memoria.
- `api/src/ethos_api/credentials/deps.py` — provider del repositorio.
- `api/src/ethos_api/credentials/router.py` — endpoints `/credentials`.
- `api/src/ethos_api/main.py` — incluir el router.
- `api/tests/test_security.py`, `api/tests/test_auth.py`,
  `api/tests/credentials/__init__.py`,
  `api/tests/credentials/test_credentials_api.py`.

Diferido: repositorio respaldado por Supabase (conexión a Postgres + estrategia
RLS, decisión por tomar); flujo OAuth/OpenID de proveedores; generalización de
categorías (D23, hoy `MediaCategory` cubre las 4 actuales, ListenBrainz=music).

## 2. Evaluación Crítica

**Veredicto: viable / bueno.** Implementa D20 (sesión + credenciales cifradas) y
respeta el guardrail D22 (estos endpoints van por HTTP autenticado, no por el
MCP). El cifrado a nivel de app (Fernet) cumple D9; la llave vive en el entorno.

Decisiones con trade-off (recomendada marcada):

1. **Verificación de sesión**:
   - (Rec.) Verificar el JWT de Supabase (HS256 con `SUPABASE_JWT_SECRET`),
     comprobando `aud="authenticated"` y extrayendo `sub` como user_id. Sin red.
   - Llamar a la API de Supabase por cada request → latencia y acoplamiento.

2. **Persistencia ahora**:
   - (Rec.) Repositorio abstracto + impl en memoria → feature completa y testeable
     sin BD; el repo Supabase (con su estrategia RLS) se añade después.
   - Ir directo a Supabase ahora → arrastra decisión de conexión/RLS no tomada.

3. **Cifrado**:
   - (Rec.) Fernet (AES-128-CBC + HMAC), llave urlsafe-base64 de 32 bytes en
     `ENCRYPTION_KEY` (la que ya generaste). Estándar y simple (D9).

**Deuda/riesgos vigilados:** sin persistencia real aún (las credenciales viven en
memoria del proceso); el repo Supabase y la estrategia RLS (service_role + filtro
por user_id vs reenvío de JWT) es el siguiente ciclo; el token plano solo existe
en memoria y nunca se devuelve en las respuestas.

## 3. Plan de Acción Detallado

### Bloque A — Datos
- [x] **Paso 1: [supabase/migrations/0002_user_credentials.sql]** tabla
  `user_credentials` (user_id, category, provider, encrypted_token, timestamps),
  `unique(user_id, provider)`, índice, trigger de `updated_at`, RLS owner-only.

### Bloque B — Configuración y dependencias
- [x] **Paso 2: [api/pyproject.toml]** añadir `cryptography` y `pyjwt` a runtime;
  configurar ruff para permitir `fastapi.Depends`/`Security` en defaults (B008).
- [x] **Paso 3: [.env.example] + [config.py]** añadir `SUPABASE_JWT_SECRET`.

### Bloque C — Seguridad
- [x] **Paso 4: [api/src/ethos_api/security.py]** `TokenCipher` (Fernet) con
  `encrypt`/`decrypt` y `get_cipher()` desde `settings.encryption_key`.
- [x] **Paso 5: [api/src/ethos_api/auth.py]** `get_current_user_id`: lee el Bearer,
  verifica el JWT (HS256, `aud="authenticated"`), devuelve `sub`; 401 si falla.

### Bloque D — Credenciales
- [x] **Paso 6: [credentials/models.py]** `ConnectCredentialInput` (provider,
  category, token), `UserCredential` (con `encrypted_token`) y `CredentialSummary`
  (sin token).
- [x] **Paso 7: [credentials/repository.py]** `CredentialRepository` (Protocol) e
  `InMemoryCredentialRepository` (upsert/list/get/delete por user_id+provider).
- [x] **Paso 8: [credentials/deps.py]** `get_repository()` (singleton en memoria).
- [x] **Paso 9: [credentials/router.py]** `POST /credentials` (cifra y guarda),
  `GET /credentials` (lista resúmenes sin token), `DELETE /credentials/{provider}`.
- [x] **Paso 10: [main.py]** incluir el router.

### Bloque E — Tests
- [x] **Paso 11: [tests/test_security.py]** roundtrip de cifrado y fallo con otra
  llave.
- [x] **Paso 12: [tests/test_auth.py]** JWT válido → user_id; sin token y firma
  inválida → 401.
- [x] **Paso 13: [tests/credentials/test_credentials_api.py]** conectar (token
  guardado cifrado, no devuelto), listar, aislamiento por usuario, requiere auth,
  desconectar.

## 4. Reporte de Pruebas

**[APROBADO]**

- Cumplimiento funcional: sesión (verificación de JWT de Supabase), cifrado
  Fernet de credenciales y endpoints `POST/GET/DELETE /credentials` sobre
  repositorio en memoria; el token se guarda cifrado y nunca se devuelve.
- Idioma del código: identificadores en inglés, comentarios en español.
- Secretos: grep sin coincidencias en `src`.
- Verificación de stack (uv): `ruff` sin issues; `mypy` sin issues (27
  archivos); `pytest` 17 passed.
- Limpieza: se usaron claves de prueba de ≥32 bytes para evitar el
  `InsecureKeyLengthWarning` de PyJWT (los secretos reales de Supabase ya lo son).
