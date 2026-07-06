// Datos de ejemplo del Detalle de categoría, copiados del prototipo
// (App Ethos.dc.html). El backend los sustituye. v1: Juegos conectada; el resto
// del catálogo, en desarrollo (D27).

export type CategoryStat = { value: string; label: string };
export type TopItem = {
  rank: number;
  name: string;
  sub: string;
  value: string;
  bar: number;
};
export type RecentItem = { name: string; sub: string; time: string };
export type Health = { label: string; state: "ok" | "warn" | "error" };

export type CategoryDetailData = {
  slug: string;
  name: string;
  accent: string;
  provider: string;
  ns: string;
  blurb: string;
  state: "live" | "soon";
  // Conectada:
  hero?: { value: string; label: string };
  spark?: number[];
  stats?: CategoryStat[];
  topTitle?: string;
  top?: TopItem[];
  recentTitle?: string;
  recent?: RecentItem[];
  tagsTitle?: string;
  tags?: string[];
  health?: Health;
  modeLabel?: string;
  freshLabel?: string;
  ctxKb?: string;
  // En desarrollo:
  soonNote?: string;
  soonEta?: string;
};

const GAMES: CategoryDetailData = {
  slug: "games",
  name: "Juegos",
  accent: "#3b82c4",
  provider: "Steam",
  ns: "games.*",
  state: "live",
  blurb: "Biblioteca, deseados, horas jugadas y % de completado por juego.",
  hero: { value: "1.840", label: "horas jugadas" },
  spark: [8, 12, 9, 16, 14, 22, 18, 26, 24, 31],
  stats: [
    { value: "312", label: "juegos" },
    { value: "1.840", label: "horas" },
    { value: "47", label: "deseados" },
    { value: "38%", label: "completado" },
  ],
  topTitle: "Top por horas",
  top: [
    { rank: 1, name: "Stardew Valley", sub: "Simulación · Indie", value: "412 h", bar: 100 },
    { rank: 2, name: "Hades", sub: "Acción · Roguelike", value: "268 h", bar: 65 },
    { rank: 3, name: "Disco Elysium", sub: "RPG narrativo", value: "141 h", bar: 34 },
    { rank: 4, name: "Hollow Knight", sub: "Metroidvania", value: "128 h", bar: 31 },
    { rank: 5, name: "Outer Wilds", sub: "Aventura", value: "96 h", bar: 23 },
  ],
  recentTitle: "Jugado recientemente",
  recent: [
    { name: "Balatro", sub: "+6,2 h esta semana", time: "hoy" },
    { name: "Tunic", sub: "+3,1 h", time: "ayer" },
    { name: "Pizza Tower", sub: "+1,4 h", time: "hace 3 d" },
  ],
  tagsTitle: "Deseados",
  tags: ["Silksong", "Hades II", "Pentiment", "Animal Well", "Slay the Spire 2"],
  health: { label: "Operativa", state: "ok" },
  modeLabel: "API · en vivo",
  freshLabel: "hace 2 h",
  ctxKb: "84 KB",
};

const MUSIC: CategoryDetailData = {
  slug: "music",
  name: "Música",
  accent: "#d8543f",
  provider: "ListenBrainz",
  ns: "music.*",
  state: "live",
  blurb: "Scrobbles, artistas y canciones más escuchadas por periodo.",
};

const FILM: CategoryDetailData = {
  slug: "film",
  name: "Cine y TV",
  accent: "#8b5cf6",
  provider: "Trakt",
  ns: "film.*",
  state: "live",
  blurb: "Películas, series, episodios y tiempo total visto.",
};

const ANIME: CategoryDetailData = {
  slug: "anime",
  name: "Anime y manga",
  accent: "#e0883c",
  provider: "AniList",
  ns: "anime.*",
  state: "live",
  blurb: "Series vistas, capítulos de manga leídos y títulos en curso.",
};

const BOOKS: CategoryDetailData = {
  slug: "books",
  name: "Libros",
  accent: "#2f9e6b",
  provider: "Goodreads",
  ns: "books.*",
  state: "live",
  blurb: "Leídos, páginas, lecturas en curso y autores más leídos.",
};

// Categorías diferidas fuera del catálogo activo (D27/D31): se muestran "en
// desarrollo" con opción de aviso (D50). El slug coincide con el id del backend.
const PLACES: CategoryDetailData = {
  slug: "places",
  name: "Lugares",
  accent: "#0ea5a4",
  provider: "Swarm",
  ns: "places.*",
  state: "soon",
  blurb: "Sitios a los que vas, guardados desde Swarm.",
  soonNote: "Sitios a los que vas, guardados desde Swarm.",
  soonEta: "en desarrollo",
};

const FOOD: CategoryDetailData = {
  slug: "food",
  name: "Comida",
  accent: "#e0663c",
  provider: "Beli",
  ns: "food.*",
  state: "soon",
  blurb: "Restaurantes y platos que puntúas en Beli.",
  soonNote: "Restaurantes y platos que puntúas en Beli.",
  soonEta: "en desarrollo",
};

const BOARD: CategoryDetailData = {
  slug: "board",
  name: "Juegos de mesa",
  accent: "#9a6b3f",
  provider: "BoardGameGeek",
  ns: "board.*",
  state: "soon",
  blurb: "Tu colección y partidas de BoardGameGeek.",
  soonNote: "Tu colección y partidas de BoardGameGeek.",
  soonEta: "en desarrollo",
};

// Las cinco categorías del catálogo están activas; las tres diferidas quedan
// "en desarrollo" con aviso (D50).
export const CATEGORY_DETAIL: Record<string, CategoryDetailData> = {
  games: GAMES,
  music: MUSIC,
  film: FILM,
  anime: ANIME,
  books: BOOKS,
  places: PLACES,
  food: FOOD,
  board: BOARD,
};

export function categoryBySlug(slug: string): CategoryDetailData | undefined {
  return CATEGORY_DETAIL[slug];
}
