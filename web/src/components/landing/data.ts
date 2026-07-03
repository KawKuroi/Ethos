// Datos de la landing, copiados del prototipo (Landing mockups.dc.html).
// Catálogo activo: las 5 categorías de D27 ajustado por D31 (Lugares, Comida y
// Juegos de mesa quedan diferidas; Actividad física retirada por falta de
// fuente viable). Anime y manga toma sus valores del prototipo de la app
// (misma fuente de verdad).

export type LandingCategory = {
  name: string;
  value: string;
  label: string;
  accent: string;
  providers: string[];
};

export const CATS: LandingCategory[] = [
  {
    name: "Juegos",
    value: "1.840",
    label: "horas jugadas",
    accent: "#3b82c4",
    providers: ["Steam", "Xbox", "PlayStation", "GOG"],
  },
  {
    name: "Música",
    value: "84.210",
    label: "scrobbles",
    accent: "#d8543f",
    providers: ["ListenBrainz", "Last.fm", "Spotify", "Apple Music"],
  },
  {
    name: "Cine y TV",
    value: "214",
    label: "títulos vistos",
    accent: "#8b5cf6",
    providers: ["Trakt", "Letterboxd", "TMDB", "IMDb"],
  },
  {
    name: "Anime y manga",
    value: "318",
    label: "episodios · año",
    accent: "#e0883c",
    providers: ["AniList", "MyAnimeList", "Kitsu"],
  },
  {
    name: "Libros",
    value: "42",
    label: "leídos · este año",
    accent: "#2f9e6b",
    providers: ["Goodreads", "StoryGraph", "Hardcover", "Open Library"],
  },
];

export const HERO_SOURCES = [
  { name: "Steam", initial: "S", accent: "#3b82c4" },
  { name: "Spotify", initial: "S", accent: "#2f9e6b" },
  { name: "AniList", initial: "A", accent: "#e0883c" },
  { name: "Trakt", initial: "T", accent: "#8b5cf6" },
  { name: "Goodreads", initial: "G", accent: "#b07b3e" },
];

export const MCP_POINTS = [
  {
    k: "Sin copiar y pegar",
    t: "Lee tu perfil solo",
    d: "Tu IA consulta Ethos directamente. No vuelcas tu historial en el chat ni lo mantienes tú a mano.",
  },
  {
    k: "Mínimo necesario",
    t: "Pide solo lo justo",
    d: "Cada pregunta viaja en kilobytes, no tu vida entera — y tú eliges qué categorías se exponen.",
  },
  {
    k: "En vivo",
    t: "Siempre al día",
    d: "Como consulta en tiempo real, tu IA siempre tiene tu última actividad sin que la refresques.",
  },
];

export const STEPS = [
  {
    n: "1",
    title: "Conecta tus apps",
    body: "Por API o subiendo un export. Una fuente por categoría, intercambiable.",
    arrow: "→",
  },
  {
    n: "2",
    title: "Ethos lo unifica",
    body: "Cada fuente se normaliza a un mismo esquema, lista para leer y consultar.",
    arrow: "→",
  },
  {
    n: "3",
    title: "Léelo tú · o dáselo a tu IA",
    body: "Explóralo en el panel, o conéctalo por MCP para que tu IA lo use.",
    arrow: "",
  },
];

export const WALK_STEPS = [
  { title: "Conectas la fuente", sub: "Steam aporta tu actividad tal cual." },
  { title: "Ethos la normaliza", sub: "Mismos campos para toda fuente." },
  { title: "Queda como categoría", sub: "Lista para ver en tu perfil." },
  { title: "Tu IA la usa", sub: "Pide solo Juegos, nada más." },
];

export const FAQS = [
  {
    q: "¿Qué hace Ethos?",
    a: "Reúne tu gusto de muchas apps en un esquema común y lo convierte en contexto para tu IA.",
  },
  {
    q: "¿Cómo se lo doy a la IA?",
    a: "Descargas los archivos y se los pasas, o conectas Ethos como servidor MCP para que lo consulte solo.",
  },
  {
    q: "¿Carga todo mi perfil cada vez?",
    a: "No. El MCP expone consultas acotadas y entrega solo lo que cada pregunta pide.",
  },
  {
    q: "¿Y si una fuente no tiene API?",
    a: "Subes su export (.json, .csv, .zip) y Ethos lo normaliza, o lo añades a mano.",
  },
];

export const GITHUB_URL = "https://github.com/KawKuroi/Ethos";
