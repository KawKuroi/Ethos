// Datos de la pantalla Inicio que aún no aporta el backend. El panorama y las
// cifras salen de los hooks de fuentes (use-active-sources); aquí quedan el
// estado del MCP y las alertas agregadas.

// TODO: sustituir por el estado real de conexión del MCP (tarea Conectar IA).
export const MCP_CONNECTED = false;

export type AlertLevel = "warn" | "error";

export type GlobalAlert = {
  id: string;
  catName: string;
  accent: string;
  level: AlertLevel;
  text: string;
  time: string;
  action?: string;
};

// Alertas agregadas (warn/error) de todas las categorías, ordenadas por
// severidad. Vacío hasta que el backend reporte alertas reales: la sección se
// oculta.
export const GLOBAL_ALERTS: GlobalAlert[] = [];
