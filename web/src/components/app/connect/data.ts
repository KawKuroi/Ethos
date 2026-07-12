// Datos del playground de Conectar IA (simulado, sin LLM en v1). El endpoint y
// el token reales los aporta el API (`lib/api`); aquí viven las guías de
// conexión por cliente y las consultas de ejemplo del playground.

export type ClientGuide = {
  id: string;
  name: string;
  steps: string[];
  command?: string; // bloque copiable (comando de terminal o JSON de config)
  note?: string;
};

// Guías por cliente. La vía principal es OAuth: el usuario pega la URL y su
// cliente lo trae a Ethos a autorizar; el token manual queda como avanzado.
export function clientGuides(endpoint: string): ClientGuide[] {
  return [
    {
      id: "claude",
      name: "Claude",
      steps: [
        "En claude.ai o en la app de escritorio, abre Ajustes → Conectores.",
        "Pulsa «Añadir conector personalizado», ponle nombre (p. ej. Ethos) y pega la URL del paso 1.",
        "Pulsa Conectar: se abrirá Ethos para que inicies sesión y autorices el acceso.",
        "En un chat nuevo, activa Ethos desde el botón + → Conectores, y pregúntale por tu gusto.",
      ],
      note: "Funciona en todos los planes de Claude; el gratuito admite un conector.",
    },
    {
      id: "claude-code",
      name: "Claude Code",
      steps: [
        "En tu terminal, ejecuta el comando de abajo.",
        "Dentro de Claude Code escribe /mcp, elige ethos y sigue el enlace para autorizar en el navegador.",
      ],
      command: `claude mcp add --transport http ethos ${endpoint}`,
    },
    {
      id: "cursor",
      name: "Cursor",
      steps: [
        "Abre Settings → MCP y pulsa «Add new MCP server» (o edita ~/.cursor/mcp.json).",
        "Pega el bloque de abajo y guarda.",
        "Cuando el servidor aparezca como «Needs login», pulsa para autorizar en el navegador.",
      ],
      command: `{\n  "mcpServers": {\n    "ethos": { "url": "${endpoint}" }\n  }\n}`,
    },
    {
      id: "otros",
      name: "Otros clientes",
      steps: [
        "Añade un servidor MCP remoto (transporte HTTP estándar) con la URL del paso 1.",
        "Si tu cliente soporta OAuth, te llevará a Ethos para autorizar: no necesitas token.",
        "Si solo admite cabeceras, genera el token manual de abajo y envíalo como «Authorization: Bearer …».",
      ],
    },
  ];
}

export type McpItem = {
  label: string;
  sub: string;
  value: string;
  bar: number | null;
};

export type McpQuery = {
  id: string;
  q: string;
  tool: string;
  args: string;
  ctx: string;
  full: string;
  pct: number;
  answer: string;
  items: McpItem[];
  response: string;
};

// Consultas de ejemplo sobre Juegos (única categoría activa en v1).
export const MCP_QUERIES: McpQuery[] = [
  {
    id: "top",
    q: "¿Mis juegos con más horas?",
    tool: "games_top_by_hours",
    args: "limit: 3",
    ctx: "0,4 KB",
    full: "84 KB",
    pct: 5,
    answer:
      "Tus juegos con más horas son Stardew Valley, Hades y Disco Elysium. Stardew destaca con diferencia, con más de 400 horas.",
    items: [
      { label: "Stardew Valley", sub: "91% completado", value: "412 h", bar: 100 },
      { label: "Hades", sub: "74% completado", value: "268 h", bar: 65 },
      { label: "Disco Elysium", sub: "100% completado", value: "141 h", bar: 34 },
    ],
    response: [
      "[",
      '  { "title": "Stardew Valley", "hours": 412, "completion": 0.91 },',
      '  { "title": "Hades",          "hours": 268, "completion": 0.74 },',
      '  { "title": "Disco Elysium",  "hours": 141, "completion": 1.00 }',
      "]",
    ].join("\n"),
  },
  {
    id: "recent",
    q: "¿Qué jugué esta semana?",
    tool: "games_recent",
    args: "days: 7",
    ctx: "0,3 KB",
    full: "84 KB",
    pct: 4,
    answer:
      "Esta semana has jugado sobre todo a Balatro, con 6,2 horas. También algo de Tunic y Pizza Tower.",
    items: [
      { label: "Balatro", sub: "roguelike de cartas", value: "+6,2 h", bar: null },
      { label: "Tunic", sub: "aventura", value: "+3,1 h", bar: null },
      { label: "Pizza Tower", sub: "plataformas", value: "+1,4 h", bar: null },
    ],
    response: [
      "[",
      '  { "title": "Balatro",     "hours_week": 6.2 },',
      '  { "title": "Tunic",       "hours_week": 3.1 },',
      '  { "title": "Pizza Tower", "hours_week": 1.4 }',
      "]",
    ].join("\n"),
  },
  {
    id: "summary",
    q: "¿Cuántos juegos tengo?",
    tool: "games_summary",
    args: "",
    ctx: "0,2 KB",
    full: "84 KB",
    pct: 3,
    answer:
      "Tienes 312 juegos en la biblioteca y 1.840 horas jugadas, con un 38% de completado medio.",
    items: [
      { label: "En biblioteca", sub: "juegos", value: "312", bar: null },
      { label: "Horas jugadas", sub: "total", value: "1.840", bar: null },
      { label: "Completado medio", sub: "por juego", value: "38%", bar: null },
    ],
    response: [
      "{",
      '  "games": 312,',
      '  "hours": 1840,',
      '  "avg_completion": 0.38,',
      '  "wishlisted": 47',
      "}",
    ].join("\n"),
  },
  {
    id: "music-top",
    q: "¿Mis artistas más escuchados?",
    tool: "music_top_artists",
    args: "limit: 3",
    ctx: "0,3 KB",
    full: "56 KB",
    pct: 4,
    answer:
      "En los últimos 30 días has escuchado sobre todo a King Gizzard, Radiohead y Khruangbin, con King Gizzard bien por delante.",
    items: [
      { label: "King Gizzard & the Lizard Wizard", sub: "142 escuchas", value: "142", bar: 100 },
      { label: "Radiohead", sub: "88 escuchas", value: "88", bar: 62 },
      { label: "Khruangbin", sub: "51 escuchas", value: "51", bar: 36 },
    ],
    response: [
      "[",
      '  { "name": "King Gizzard & the Lizard Wizard", "count": 142 },',
      '  { "name": "Radiohead",  "count": 88 },',
      '  { "name": "Khruangbin", "count": 51 }',
      "]",
    ].join("\n"),
  },
  {
    id: "film-top",
    q: "¿Mis películas más vistas?",
    tool: "film_top_movies",
    args: "limit: 3",
    ctx: "0,3 KB",
    full: "41 KB",
    pct: 4,
    answer:
      "Tus películas más repetidas son Inception, Interstellar y Arrival. Inception la has visto tres veces.",
    items: [
      { label: "Inception", sub: "2010", value: "3 veces", bar: 100 },
      { label: "Interstellar", sub: "2014", value: "2 veces", bar: 66 },
      { label: "Arrival", sub: "2016", value: "1 vez", bar: 33 },
    ],
    response: [
      "[",
      '  { "title": "Inception",    "year": 2010, "plays": 3 },',
      '  { "title": "Interstellar", "year": 2014, "plays": 2 },',
      '  { "title": "Arrival",      "year": 2016, "plays": 1 }',
      "]",
    ].join("\n"),
  },
  {
    id: "anime-top",
    q: "¿Mis animes mejor puntuados?",
    tool: "anime_top_rated",
    args: "limit: 3",
    ctx: "0,3 KB",
    full: "38 KB",
    pct: 4,
    answer:
      "Tus mejor puntuados son Berserk (100), Fullmetal Alchemist: Brotherhood (95) y Shingeki no Kyojin (90).",
    items: [
      { label: "Berserk", sub: "manga", value: "100", bar: 100 },
      { label: "Fullmetal Alchemist: Brotherhood", sub: "anime", value: "95", bar: 95 },
      { label: "Shingeki no Kyojin", sub: "anime", value: "90", bar: 90 },
    ],
    response: [
      "[",
      '  { "title": "Berserk",                          "score": 100 },',
      '  { "title": "Fullmetal Alchemist: Brotherhood", "score": 95 },',
      '  { "title": "Shingeki no Kyojin",               "score": 90 }',
      "]",
    ].join("\n"),
  },
  {
    id: "books-current",
    q: "¿Qué estoy leyendo?",
    tool: "books_currently_reading",
    args: "",
    ctx: "0,2 KB",
    full: "33 KB",
    pct: 3,
    answer:
      "Ahora mismo estás con Project Hail Mary, de Andy Weir. Es tu única lectura en curso.",
    items: [
      { label: "Project Hail Mary", sub: "Andy Weir", value: "en curso", bar: null },
    ],
    response: [
      "[",
      '  { "title": "Project Hail Mary", "author": "Andy Weir" }',
      "]",
    ].join("\n"),
  },
];

const GAMES_QUERY = MCP_QUERIES.find((q) => q.id === "top") as McpQuery;
const MUSIC_QUERY = MCP_QUERIES.find((q) => q.id === "music-top") as McpQuery;
const FILM_QUERY = MCP_QUERIES.find((q) => q.id === "film-top") as McpQuery;
const ANIME_QUERY = MCP_QUERIES.find((q) => q.id === "anime-top") as McpQuery;
const BOOKS_QUERY = MCP_QUERIES.find((q) => q.id === "books-current") as McpQuery;

// Respuesta simulada cuando la consulta no encaja con una categoría activa.
export function missQuery(text: string): McpQuery {
  return {
    id: "miss",
    q: text,
    tool: "profile_search",
    args: `q: "${text.slice(0, 16).replace(/"/g, "")}…"`,
    ctx: "0,2 KB",
    full: "84 KB",
    pct: 3,
    answer:
      "Consulté tu perfil con una tool acotada, pero no reconocí la consulta. Prueba a preguntar por tus juegos, tu música, tu cine, tu anime o tus libros.",
    items: [],
    response:
      '{\n  "matched": false,\n  "hint": "categorías: games, music, film, anime, books"\n}',
  };
}

// Palabras clave por categoría para el matching sencillo (sin LLM).
const KEYWORDS: [McpQuery, string[]][] = [
  [GAMES_QUERY, ["juego", "games", "steam", "hora"]],
  [
    MUSIC_QUERY,
    ["músic", "music", "artista", "escuch", "canci", "scrobble", "listenbrainz"],
  ],
  [FILM_QUERY, ["pel", "serie", "cine", "film", "episodio", "trakt", "vist"]],
  [ANIME_QUERY, ["anime", "manga", "anilist", "capítulo", "capitulo", "otaku"]],
  [BOOKS_QUERY, ["libro", "leyendo", "leído", "leido", "autor", "goodreads", "págin", "pagin"]],
];

// Matching sencillo (sin LLM): enruta la consulta a la categoría activa.
export function matchQuery(text: string): McpQuery {
  const t = text.toLowerCase();
  for (const [query, keywords] of KEYWORDS) {
    if (keywords.some((k) => t.includes(k))) {
      return { ...query, q: text };
    }
  }
  return missQuery(text);
}
