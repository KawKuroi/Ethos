# ACTIVE_TASK — Revisión de seguridad + planificación (auth/sesión y categorías)

Tarea: 1) revisar la seguridad de todo lo construido; 2) planificar la sesión de
usuario y el almacenamiento cifrado de credenciales de terceros ("guardar las
APIs"); 3) planificar el modelo para incorporar las categorías que aún no están.
Es planificación + revisión: se actualizan docs y se registran decisiones y
guardrails; la implementación de esas features llega en tareas posteriores.

## 1. Contexto y Archivos Afectados

Revisión sobre el código actual de `/api` y `/supabase` (sin cambios de código:
la revisión no encontró vulnerabilidad activa que corregir ya). Cambios en docs:

- `docs/architecture.md` — registro de conectores; guardrail de auth del MCP;
  flujo de sesión y almacenamiento cifrado de credenciales.
- `docs/data-model.md` — tabla planificada `user_credentials` y nota de registro.
- `docs/decisions.md` — D20 (sesión + credenciales cifradas), D21 (registro de
  conectores), D22 (auth del MCP antes de tools de datos).
- `docs/roadmap.md` — tareas de auth/sesión, credenciales, middleware MCP y
  registro de conectores.
- `docs/current.md` — snapshot de seguridad y bitácora.

## 2. Evaluación Crítica

**Veredicto: viable.** Planificación bien anclada en lo ya documentado (D6, D8,
D9) y en el modelo de conectores; sin invenciones. La revisión confirma que el
código actual no tiene vulnerabilidades activas; los pendientes son de diseño y
quedan con guardrails para no introducir riesgo al implementarlos.

Decisiones con trade-off (recomendada marcada):

1. **Almacenamiento de credenciales de terceros**:
   - (Rec.) Tabla `user_credentials` con token cifrado a nivel de app
     (Fernet/AES-GCM), llave en secret manager, RLS owner-only (coherente con D9).
   - Guardar en texto plano o en el cliente → inseguro; descartado.

2. **Extensión de categorías/proveedores**:
   - (Rec.) Registro de conectores (registry) por (categoría, proveedor) con
     `capabilities`; las capas río abajo resuelven por el registro.
   - Condicionales/if por proveedor → acopla y no escala; descartado.

3. **Auth del MCP**:
   - (Rec.) Middleware de token por usuario (D8); hasta tenerlo, solo tools no
     sensibles (hoy `ping`).
   - Exponer tools de datos sin auth → fuga de datos; prohibido (guardrail D22).

**Deuda/riesgos vigilados:** cifrado de credenciales y middleware MCP están
diseñados pero no implementados; RLS debe replicarse en toda tabla nueva; CORS
deberá restringirse al integrar `/web`.

## 3. Plan de Acción Detallado

### Bloque A — Revisión de seguridad
- [x] **Paso 1: [revisión]** auditar `/api` y `/supabase` (secretos, RLS, fugas
  de credenciales, timeouts, auth del MCP); reportar hallazgos. Sin fix de código
  porque no hay vulnerabilidad activa; los pendientes pasan a plan/guardrails.

### Bloque B — Diseño de sesión y credenciales
- [x] **Paso 2: [docs/architecture.md]** añadir el flujo: Supabase Auth (sesión)
  → la app guarda credenciales de terceros cifradas → se descifran solo en
  memoria al llamar la API; el token del MCP nunca se reenvía a terceros.
- [x] **Paso 3: [docs/data-model.md]** especificar la tabla planificada
  `user_credentials` (user_id, category, provider, encrypted_token, timestamps)
  con RLS owner-only.

### Bloque C — Extensión de categorías
- [x] **Paso 4: [docs/architecture.md]** detallar el registro de conectores y el
  catálogo completo de 9 categorías (Juegos, Música, Cine y TV, Anime y manga,
  Actividad física, Libros, Lugares, Comida, Juegos de mesa) con proveedor y
  modo; señalar la generalización del contrato (Actividad física = evento/métrica).

### Bloque D — Decisiones y roadmap
- [x] **Paso 5: [docs/decisions.md]** añadir D20, D21, D22 y D23 (catálogo de
  categorías y generalización del contrato).
- [x] **Paso 6: [docs/roadmap.md]** añadir a Fase 1 las tareas de sesión +
  credenciales cifradas, middleware de auth del MCP, y registro de conectores.

### Bloque E — Estado
- [x] **Paso 7: [docs/current.md]** snapshot de seguridad y entrada de bitácora.

## 4. Reporte de Pruebas

**[APROBADO]**

- Cumplimiento funcional: revisión de seguridad hecha + planificación (sesión y
  credenciales cifradas, registro de conectores, catálogo de 9 categorías y
  generalización del contrato) documentada en architecture/data-model/decisions/
  roadmap.
- Idioma: docs en español; sin cambios de código.
- Secretos: grep sin coincidencias en `/docs`.
- Verificación de stack: sin cambios de código; suite reverificada
  (`pytest` 8 passed) para confirmar que nada se rompió.
- Revisión de seguridad: sin vulnerabilidad activa en el código actual; los
  pendientes (cifrado de credenciales, middleware del MCP) quedan planificados y
  con guardrail (D22).
