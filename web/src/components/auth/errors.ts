// Mensajes de error compartidos por los formularios de auth.

// Distingue la configuración ausente (env vars de Supabase sin poblar, un
// pendiente de despliegue) de un fallo real de red, para no disfrazar lo
// primero de "revisa tu conexión".
export function connectionMessage(err: unknown): string {
  if (err instanceof Error && err.message.includes("NEXT_PUBLIC_SUPABASE")) {
    return "La web aún no tiene configurada la conexión con el servidor (variables de entorno). No es un problema de tu red.";
  }
  return "No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.";
}
