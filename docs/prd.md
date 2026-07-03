# PRD — Contexto

## 1. Problema

Las IA no conocen el gusto real de una persona, y los datos que lo describen están dispersos en plataformas cerradas (Steam, ListenBrainz, Trakt, Goodreads, etc.), cada una con su propio formato y su propia forma de acceso. No existe una capa única que normalice esa información y la entregue a una IA de forma consultable y controlada.

## 2. Objetivos

- Reunir la información de tracking de una persona en un almacén normalizado e indexado.
- Entregar ese contexto a cualquier IA de dos formas (D24): archivos de contexto descargables por categoría, o un servidor MCP que lo sirve en vivo con consultas acotadas.
- Permitir consultas eficientes y acotadas (por ejemplo, "mis canciones más escuchadas de los últimos 30 días") sin cargar todo el contexto; hacer visible cuánto contexto viaja en cada consulta ("0,4 KB de 84 KB").
- Dar a la persona un panel visual para ver y controlar qué contexto existe y qué se entrega.

## 3. No objetivos (por ahora)

- No es una red social ni tiene recomendaciones propias.
- No busca tiempo real; la información se actualiza bajo demanda.
- No reemplaza a las plataformas de origen.

## 4. Usuarios

- Primario: la propia persona (uso personal), que conecta sus cuentas y consulta su gusto vía IA.
- Secundario: cualquier usuario que quiera lo mismo. La app debe ser usable sin conocimiento técnico, salvo el paso de conectar la IA, que se guía dentro de la app.

## 5. Conceptos centrales

- Categoría: dominio de gusto. Cinco en catálogo (D27, ajustado por D31): Juegos, Música, Cine y TV, Anime y manga y Libros. Diferidas: Lugares, Comida y Juegos de mesa (y Pódcasts/YouTube del prototipo). Retirada: Actividad física (D31, sin fuente viable). Estados: activa, apagada (existe sin datos) o en desarrollo (conector no listo). El catálogo se habilita secuencialmente: cada categoría se construye, prueba y confirma antes de pasar a la siguiente; las no implementadas aparecen "en desarrollo".
- Proveedor: la plataforma concreta de una categoría (ej. Steam para Juegos). Una sola activa por categoría, intercambiable entre alternativas.
- Modo de conexión: API (donde exista) o import (subir el export, con guía por proveedor).
- Perfil: el conjunto normalizado de la persona, base de las dos salidas.
- Contexto: la vista del perfil lista para una IA. Por categoría, descargable como archivo (`<categoria>.context.json`) o servido en vivo por el MCP.
- Servidor MCP: expone el perfil a la IA (resumen + tools de consulta con namespace por categoría).
- Panel: la interfaz visual de la persona (pantallas Inicio, Detalle de categoría, Fuentes, Conectar IA, Ayuda, Ajustes).

La UI está completamente especificada en el diseño de Claude Design (ver `design.md`, D25); ese prototipo manda sobre cualquier descripción textual.

## 6. Requisitos funcionales

- Cuenta y autenticación de usuario: correo/contraseña, Google y GitHub, con recuperación de contraseña (D26).
- Por cada categoría: elegir proveedor y modo (API o import); conectar; cambiar de proveedor, preguntando si se conserva el histórico o se reemplaza.
- Extracción de datos (vía API o parseo de import) y normalización a un esquema común.
- Almacenamiento normalizado e indexado, multiusuario y aislado por usuario.
- Refresco bajo demanda para fuentes API (por categoría y global), asíncrono, con estado visible.
- Panel visual según el diseño: Inicio (cifras del gusto, panorama de categorías, alertas agregadas, actividad reciente), Detalle por categoría (stats, destacados, recientes, listas, conexión), Fuentes (salud y método por categoría) y Ajustes (perfil, zona horaria, tema, borrado de datos y de cuenta con 30 días para deshacer).
- Descarga de contexto por categoría con vista previa (JSON / MCP) desde el detalle.
- Servidor MCP con resumen (resource) y tools de consulta parametrizadas, con token por usuario.
- Pantalla Conectar IA: endpoint y token del usuario, guía de tres pasos y playground que demuestra la tool llamada, el contexto que viaja y la respuesta cruda.
- Alertas por fuente (token por caducar, sync fallida, datos sin actualizar) con acción directa, agregadas en Inicio.
- Sección de ayuda: FAQ, formulario de sugerencias (categoría + tipo + texto) y contacto; recordatorio persistente mientras la IA no esté conectada.
- Landing pública con las dos salidas, el catálogo de categorías, cómo se usa, FAQ y sugerencias.
- Tema claro / oscuro / sistema persistido; animaciones desactivables con `prefers-reduced-motion`.

## 7. Requisitos no funcionales

- Hospedado en su totalidad; costo objetivo 0 USD/mes.
- Seguridad: tokens de terceros cifrados en reposo; aislamiento por usuario; el token de auth del MCP nunca se reenvía a APIs externas.
- Rendimiento: consultas del MCP acotadas e indexadas; no cargar contexto innecesario.
- Cobertura de tests en todas las capas.

## 8. Alcance de la v1 (slice vertical: Juegos / Steam)

Incluye: conexión de Steam (OpenID) con manejo de perfil privado; extracción de biblioteca, deseados, horas de juego, porcentaje de completado agregado por juego y datos de perfil; almacenamiento indexado; tools del MCP de juegos; descarga del contexto de juegos; la web del slice con el diseño final (auth, Inicio, Detalle de Juegos, Fuentes, Conectar IA, Ayuda, Ajustes) y la landing, con Juegos como única categoría activa y las otras cuatro visibles como "en desarrollo"; refresco asíncrono; estados de frescura.

Fuera de la v1: detalle de logros individuales, géneros (diferido), resto de categorías, OAuth 2.1 para el MCP, entradas a mano, playground con LLM real (la v1 lo simula con datos reales, como el prototipo).

## 9. Criterios de éxito de la v1

- La persona conecta Steam en un clic y ve sus estadísticas en el panel con el diseño final.
- Una IA conectada al MCP responde correctamente consultas como "mis juegos con más horas" o "qué jugué recientemente" sin cargar toda la biblioteca.
- El contexto de juegos se puede descargar como archivo y pasar a cualquier IA.
- El refresco actualiza los datos sin bloquear la interfaz y el estado de frescura lo refleja.
- Todas las capas tienen tests que pasan en CI.
