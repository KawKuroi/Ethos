// Datos de ejemplo de la pantalla Inicio, copiados del prototipo
// (App Ethos.dc.html). El backend los sustituye al implementar el slice de
// Steam. v1: Juegos activa; el resto del catálogo, en desarrollo (D27).

// TODO: sustituir por el estado real de conexión del MCP (tarea Conectar IA).
export const MCP_CONNECTED = false;

export type OvStat = { value: string; label: string };

export const OV_STATS: OvStat[] = [
  { value: "312", label: "juegos" },
  { value: "1.840", label: "horas" },
  { value: "47", label: "deseados" },
  { value: "38%", label: "completado" },
];

export const OV_META = "1 fuente activa · Steam";

export type PanoramaState = "live" | "soon";

export type PanoramaRow = {
  id: string;
  name: string;
  initial: string;
  accent: string;
  provider: string;
  modeLabel: string;
  state: PanoramaState;
  heroValue: string;
  heroLabel: string;
  barPct: number; // 0-100, relativo al máximo de las activas
};

export const PANORAMA: PanoramaRow[] = [
  {
    id: "games",
    name: "Juegos",
    initial: "J",
    accent: "#3b82c4",
    provider: "Steam",
    modeLabel: "API",
    state: "live",
    heroValue: "1.840",
    heroLabel: "horas jugadas",
    barPct: 100,
  },
  {
    id: "music",
    name: "Música",
    initial: "M",
    accent: "#d8543f",
    provider: "ListenBrainz",
    modeLabel: "API",
    state: "soon",
    heroValue: "—",
    heroLabel: "",
    barPct: 0,
  },
  {
    id: "film",
    name: "Cine y TV",
    initial: "C",
    accent: "#8b5cf6",
    provider: "Trakt",
    modeLabel: "API",
    state: "soon",
    heroValue: "—",
    heroLabel: "",
    barPct: 0,
  },
  {
    id: "anime",
    name: "Anime y manga",
    initial: "A",
    accent: "#e0883c",
    provider: "AniList",
    modeLabel: "API",
    state: "soon",
    heroValue: "—",
    heroLabel: "",
    barPct: 0,
  },
  {
    id: "books",
    name: "Libros",
    initial: "L",
    accent: "#2f9e6b",
    provider: "Goodreads",
    modeLabel: "Import",
    state: "soon",
    heroValue: "—",
    heroLabel: "",
    barPct: 0,
  },
];

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
// oculta. Juegos hoy solo tendría una alerta `info`, que no se agrega.
export const GLOBAL_ALERTS: GlobalAlert[] = [];

export type ActivityItem = {
  id: string;
  text: string;
  catName: string;
  accent: string;
  time: string;
};

export const ACTIVITY: ActivityItem[] = [
  {
    id: "a1",
    text: "Jugaste a Balatro · +6,2 h",
    catName: "Juegos",
    accent: "#3b82c4",
    time: "hoy 19:40",
  },
  {
    id: "a2",
    text: "Jugaste a Tunic · +3,1 h",
    catName: "Juegos",
    accent: "#3b82c4",
    time: "ayer",
  },
  {
    id: "a3",
    text: "Jugaste a Pizza Tower · +1,4 h",
    catName: "Juegos",
    accent: "#3b82c4",
    time: "hace 3 d",
  },
];
