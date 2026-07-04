// Datos del playground de Conectar IA (simulado, sin LLM en v1). El endpoint y
// el token reales los aporta el API (`lib/api`); aquí solo viven los pasos y las
// consultas de ejemplo del playground.

export type Step = { n: number; title: string; body: string };

export const STEPS: Step[] = [
  {
    n: 1,
    title: "Abre tu cliente de IA",
    body: "En un cliente con soporte MCP (Claude u otro), añade un servidor nuevo.",
  },
  {
    n: 2,
    title: "Pega el endpoint y el token",
    body: "Usa los datos de arriba para autenticar la conexión con tu perfil.",
  },
  {
    n: 3,
    title: "Pregúntale",
    body: "Tu IA ya puede consultar tu gusto con tools acotadas, sin volcarlo entero.",
  },
];

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
    tool: "games.top_by_hours",
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
    tool: "games.recent",
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
    tool: "games.summary",
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
];

// Respuesta simulada cuando la consulta no encaja con una categoría activa.
export function missQuery(text: string): McpQuery {
  return {
    id: "miss",
    q: text,
    tool: "profile.search",
    args: `q: "${text.slice(0, 16).replace(/"/g, "")}…"`,
    ctx: "0,2 KB",
    full: "84 KB",
    pct: 3,
    answer:
      "Consulté tu perfil con una tool acotada, pero por ahora solo Juegos está activa. Prueba a preguntar por tus juegos: horas, recientes o biblioteca.",
    items: [],
    response: '{\n  "matched": false,\n  "hint": "solo Juegos está activa en la v1"\n}',
  };
}

// Matching sencillo (sin LLM): consultas sobre juegos → resumen de Juegos.
export function matchQuery(text: string): McpQuery {
  const t = text.toLowerCase();
  if (t.includes("juego") || t.includes("games") || t.includes("steam")) {
    return { ...MCP_QUERIES[0], q: text };
  }
  return missQuery(text);
}
