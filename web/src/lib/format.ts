// Formato compartido por las pantallas del panel.

// Tiempo relativo en español ("hace 2 h") desde un ISO 8601.
export function relativeTime(iso: string | null): string {
  if (!iso) return "—";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "hace un momento";
  if (mins < 60) return `hace ${mins} min`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `hace ${hours} h`;
  return `hace ${Math.round(hours / 24)} d`;
}

// Entero con separador de miles es-ES ("1.840").
export function fmtInt(n: number): string {
  return Math.round(n).toLocaleString("es-ES");
}
