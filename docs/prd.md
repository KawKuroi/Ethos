# PRD — Contexto

## 1. Problema

Las IA no conocen el gusto real de una persona, y los datos que lo describen están dispersos en plataformas cerradas (Steam, ListenBrainz, Trakt, Goodreads, etc.), cada una con su propio formato y su propia forma de acceso. No existe una capa única que normalice esa información y la entregue a una IA de forma consultable y controlada.

## 2. Objetivos

- Reunir la información de tracking de una persona en un almacén normalizado e indexado.
- Entregar esa información a cualquier IA mediante un servidor MCP, sin manipulación manual de archivos.
- Permitir consultas eficientes y acotadas (por ejemplo, "mis canciones más escuchadas de los últimos 30 días") sin cargar todo el contexto.
- Dar a la persona un panel visual para ver y controlar qué contexto existe y qué se entrega.

## 3. No objetivos (por ahora)

- No es una red social ni tiene recomendaciones propias.
- No busca tiempo real; la información se actualiza bajo demanda.
- No reemplaza a las plataformas de origen.

## 4. Usuarios

- Primario: la propia persona (uso personal), que conecta sus cuentas y consulta su gusto vía IA.
- Secundario: cualquier usuario que quiera lo mismo. La app debe ser usable sin conocimiento técnico, salvo el paso de conectar la IA, que se guía dentro de la app.

## 5. Conceptos centrales

- Categoría: dominio de medios (Música, Cine/TV, Libros, Juegos).
- Proveedor: la plataforma concreta de una categoría (ej. Steam para Juegos). Una sola activa por categoría, intercambiable.
- Modo de conexión: API (donde exista) o import (subir el export). El usuario elige.
- Perfil: el conjunto normalizado de la persona, base de las dos salidas.
- Servidor MCP: expone el perfil a la IA (resumen + tools de consulta).
- Dump: el panel visual de la persona.

## 6. Requisitos funcionales

- Cuenta y autenticación de usuario.
- Por cada categoría: elegir proveedor y modo (API o import); conectar; cambiar de proveedor, preguntando si se conserva el histórico o se reemplaza.
- Extracción de datos (vía API o parseo de import) y normalización a un esquema común.
- Almacenamiento normalizado e indexado, multiusuario y aislado por usuario.
- Refresco bajo demanda para fuentes API, asíncrono, con estado visible.
- Panel visual (dump) con estadísticas y estados de frescura por fuente.
- Servidor MCP con resumen (resource) y tools de consulta parametrizadas.
- Sección de ayuda dentro de la app: qué es, qué hace, qué no hace con los datos, y guía paso a paso para conectar la IA, con recordatorio mientras no esté conectada.

## 7. Requisitos no funcionales

- Hospedado en su totalidad; costo objetivo 0 USD/mes.
- Seguridad: tokens de terceros cifrados en reposo; aislamiento por usuario; el token de auth del MCP nunca se reenvía a APIs externas.
- Rendimiento: consultas del MCP acotadas e indexadas; no cargar contexto innecesario.
- Cobertura de tests en todas las capas.

## 8. Alcance de la v1 (slice vertical: Juegos / Steam)

Incluye: login con Steam (OpenID), extracción de biblioteca, deseados, horas de juego, porcentaje de completado agregado por juego y datos de perfil; almacenamiento indexado; tools del MCP para juegos; panel de estadísticas; refresco asíncrono; estados de frescura.

Fuera de la v1: detalle de logros individuales, géneros (diferido), resto de categorías, OAuth 2.1 para el MCP.

## 9. Criterios de éxito de la v1

- La persona conecta Steam en un clic y ve sus estadísticas.
- Una IA conectada al MCP responde correctamente consultas como "mis juegos con más horas" o "qué jugué recientemente" sin cargar toda la biblioteca.
- El refresco actualiza los datos sin bloquear la interfaz y el estado de frescura lo refleja.
- Todas las capas tienen tests que pasan en CI.
