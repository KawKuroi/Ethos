// Datos de la pantalla Inicio que aún no aporta el backend. El panorama, las
// cifras y el estado del MCP salen de sus hooks (use-active-sources,
// use-mcp-status); aquí quedan las alertas agregadas.

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
