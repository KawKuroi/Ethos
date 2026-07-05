import { getBrowserClient } from "@/lib/supabase/client";

// Cliente del backend de Ethos. Adjunta el access_token de la sesión de
// Supabase como Bearer; el API lo verifica (JWKS) y acota cada consulta por
// usuario. Pensado para usarse desde client components.

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class NotAuthenticatedError extends Error {
  constructor() {
    super("No hay sesión activa.");
    this.name = "NotAuthenticatedError";
  }
}

function baseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) throw new Error("Falta configurar NEXT_PUBLIC_API_URL.");
  return url.replace(/\/$/, "");
}

async function accessToken(): Promise<string> {
  const {
    data: { session },
  } = await getBrowserClient().auth.getSession();
  if (!session) throw new NotAuthenticatedError();
  return session.access_token;
}

async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = await accessToken();
  const response = await fetch(`${baseUrl()}${path}`, {
    ...init,
    headers: {
      ...init.headers,
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new ApiError(`El API respondió ${response.status}`, response.status);
  }
  return response;
}

async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await apiFetch(path, init);
  return (await response.json()) as T;
}

// ===== Tipos del contrato con el backend =====

export type SyncState = "never" | "syncing" | "fresh" | "private" | "error";

// Alias histórico; la fuente de juegos usa el mismo conjunto de estados.
export type GamesSyncState = SyncState;

export type TopGame = {
  title: string;
  hours: number;
  completion_pct: number | null;
};

export type RecentGame = {
  title: string;
  hours_2weeks: number;
};

export type GamesSummary = {
  games: number;
  hours: number;
  wishlisted: number;
  avg_completion_pct: number | null;
  top_by_hours: TopGame[];
  recently_played: RecentGame[];
  persona_name: string | null;
  last_synced_at: string | null;
};

export type GamesSource = {
  state: GamesSyncState;
  synced_at: string | null;
  detail: string | null;
  persona_name: string | null;
  summary: GamesSummary | null;
};

export type McpToken = {
  token: string;
  endpoint: string;
};

export type MusicTopEntry = {
  name: string;
  count: number;
};

export type MusicSummary = {
  scrobbles_total: number;
  scrobbles_window: number;
  window_days: number;
  top_artists: MusicTopEntry[];
  top_tracks: MusicTopEntry[];
  last_listened_at: string | null;
};

export type MusicSource = {
  state: SyncState;
  synced_at: string | null;
  detail: string | null;
  summary: MusicSummary | null;
};

// ===== Operaciones =====

export function getGamesSource(): Promise<GamesSource> {
  return apiJson<GamesSource>("/sources/games");
}

export function refreshSteam(): Promise<void> {
  return apiFetch("/sources/steam/refresh", { method: "POST" }).then(() => undefined);
}

// Emite (y rota) el token del MCP; el claro solo se devuelve aquí, una vez.
export function issueMcpToken(): Promise<McpToken> {
  return apiJson<McpToken>("/mcp-token", { method: "POST" });
}

// Endpoint del MCP por usuario, construido sin llamar al API.
export function mcpEndpoint(): string {
  return `${baseUrl()}/mcp/`;
}

export async function getSteamLoginUrl(returnTo: string): Promise<string> {
  const { url } = await apiJson<{ url: string }>(
    `/sources/steam/login?return_to=${encodeURIComponent(returnTo)}`,
  );
  return url;
}

export function connectSteam(params: Record<string, string>): Promise<void> {
  return apiFetch("/sources/steam", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params }),
  }).then(() => undefined);
}

// Descarga `games.context.json` disparando el guardado en el navegador.
export async function downloadGamesContext(): Promise<void> {
  const response = await apiFetch("/context/games");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "games.context.json";
  a.click();
  URL.revokeObjectURL(url);
}

export async function getGamesContextText(): Promise<string> {
  const response = await apiFetch("/context/games");
  return JSON.stringify(await response.json(), null, 2);
}

// ===== Música / ListenBrainz =====

export function getMusicSource(): Promise<MusicSource> {
  return apiJson<MusicSource>("/sources/music");
}

// Conecta ListenBrainz por username público (D37) y encola el primer refresco.
export function connectListenBrainz(userName: string): Promise<void> {
  return apiFetch("/sources/listenbrainz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name: userName }),
  }).then(() => undefined);
}

export function refreshListenBrainz(): Promise<void> {
  return apiFetch("/sources/listenbrainz/refresh", { method: "POST" }).then(
    () => undefined,
  );
}

// Descarga `music.context.json` disparando el guardado en el navegador.
export async function downloadMusicContext(): Promise<void> {
  const response = await apiFetch("/context/music");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "music.context.json";
  a.click();
  URL.revokeObjectURL(url);
}

export async function getMusicContextText(): Promise<string> {
  const response = await apiFetch("/context/music");
  return JSON.stringify(await response.json(), null, 2);
}
