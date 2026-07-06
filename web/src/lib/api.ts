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
    // El backend responde errores con `detail` legible (p. ej. la guía de un
    // import rechazado); si existe, se muestra ese texto.
    let message = `El API respondió ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string" && body.detail) message = body.detail;
    } catch {
      // Cuerpo no JSON: se conserva el mensaje genérico.
    }
    throw new ApiError(message, response.status);
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

export type TopMovie = {
  title: string;
  year: number | null;
  plays: number;
};

export type TopShow = {
  title: string;
  episodes_watched: number;
};

export type RecentWatch = {
  title: string;
  media_type: string;
  watched_at: string | null;
};

export type FilmSummary = {
  movies_watched: number;
  shows_watched: number;
  episodes_watched: number;
  hours: number;
  top_movies: TopMovie[];
  top_shows: TopShow[];
  recently_watched: RecentWatch[];
  last_synced_at: string | null;
};

export type FilmSource = {
  state: SyncState;
  synced_at: string | null;
  detail: string | null;
  summary: FilmSummary | null;
};

export type AnimeTopRated = {
  title: string;
  media_type: string;
  score: number;
  progress: number;
};

export type AnimeCurrent = {
  title: string;
  media_type: string;
  progress: number;
};

export type AnimeSummary = {
  anime_watched: number;
  manga_read: number;
  episodes_watched: number;
  chapters_read: number;
  mean_score: number | null;
  top_rated: AnimeTopRated[];
  current: AnimeCurrent[];
  last_synced_at: string | null;
};

export type AnimeSource = {
  state: SyncState;
  synced_at: string | null;
  detail: string | null;
  summary: AnimeSummary | null;
};

export type TopAuthor = {
  name: string;
  books: number;
};

export type CurrentBook = {
  title: string;
  author: string;
};

export type RecentRead = {
  title: string;
  author: string;
  finished_at: string | null;
  rating: number | null;
};

export type BooksSummary = {
  books_read: number;
  pages_read: number;
  currently_reading: CurrentBook[];
  wishlisted: number;
  top_authors: TopAuthor[];
  recent_reads: RecentRead[];
  last_synced_at: string | null;
};

export type BooksSource = {
  state: SyncState;
  synced_at: string | null;
  detail: string | null;
  summary: BooksSummary | null;
};

export type ImportResult = {
  provider: string;
  category: string;
  status: string;
  items: number;
};

// ===== Interés en categorías en desarrollo (D50) =====

// Registra un correo para avisar cuando una categoría diferida se active.
// Público: usable desde la landing sin sesión; si hay sesión, adjunta el token
// para que el backend asocie el usuario (endpoint /category-interest).
export async function registerCategoryInterest(
  category: string,
  email: string,
): Promise<void> {
  const {
    data: { session },
  } = await getBrowserClient().auth.getSession();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (session) headers.Authorization = `Bearer ${session.access_token}`;

  const response = await fetch(`${baseUrl()}/category-interest`, {
    method: "POST",
    headers,
    body: JSON.stringify({ category, email }),
  });
  if (!response.ok) {
    let message = `El API respondió ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string" && body.detail) message = body.detail;
    } catch {
      // Cuerpo no JSON: se conserva el mensaje genérico.
    }
    throw new ApiError(message, response.status);
  }
}

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

// ===== Contexto descargable (genérico por categoría) =====

// Descarga `<slug>.context.json` disparando el guardado en el navegador.
export async function downloadContext(slug: string): Promise<void> {
  const response = await apiFetch(`/context/${slug}`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${slug}.context.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function getContextText(slug: string): Promise<string> {
  const response = await apiFetch(`/context/${slug}`);
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

// ===== Cine y TV / Trakt =====

export function getFilmSource(): Promise<FilmSource> {
  return apiJson<FilmSource>("/sources/film");
}

// Conecta Trakt por username público (D41) y encola el primer refresco.
export function connectTrakt(userName: string): Promise<void> {
  return apiFetch("/sources/trakt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name: userName }),
  }).then(() => undefined);
}

export function refreshTrakt(): Promise<void> {
  return apiFetch("/sources/trakt/refresh", { method: "POST" }).then(() => undefined);
}

// ===== Anime y manga / AniList =====

export function getAnimeSource(): Promise<AnimeSource> {
  return apiJson<AnimeSource>("/sources/anime");
}

// Conecta AniList por username público (D45) y encola el primer refresco.
export function connectAniList(userName: string): Promise<void> {
  return apiFetch("/sources/anilist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name: userName }),
  }).then(() => undefined);
}

export function refreshAniList(): Promise<void> {
  return apiFetch("/sources/anilist/refresh", { method: "POST" }).then(() => undefined);
}

// ===== Libros / import (Goodreads) =====

export function getBooksSource(): Promise<BooksSource> {
  return apiJson<BooksSource>("/sources/books");
}

// Sube un export como texto al import genérico: el backend detecta el
// proveedor por la firma del archivo (D49) y ejecuta su flujo.
export function importFile(text: string): Promise<ImportResult> {
  return apiJson<ImportResult>("/imports", {
    method: "POST",
    headers: { "Content-Type": "text/csv" },
    body: text,
  });
}
