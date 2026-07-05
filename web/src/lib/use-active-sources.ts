"use client";

import type { GamesSummary } from "@/lib/api";
import { useAnimeSource } from "@/lib/use-anime-source";
import { useBooksSource } from "@/lib/use-books-source";
import { useFilmSource } from "@/lib/use-film-source";
import { useGamesSource } from "@/lib/use-games-source";
import { useMusicSource } from "@/lib/use-music-source";

// Vista homogénea de cada categoría activable para Inicio y Fuentes: el hook
// resuelve los cinco endpoints y entrega la métrica hero y las etiquetas ya
// calculadas, de modo que las pantallas rendericen con un componente único
// por estado en vez de una copia por categoría.

export type ActiveSourceView = {
  slug: string;
  name: string;
  initial: string;
  accent: string;
  provider: string;
  modeLabel: "API" | "Import";
  live: boolean;
  syncing: boolean;
  // Métrica hero de la fila del panorama ("1.840" + "horas jugadas").
  heroValue: number;
  heroLabel: string;
  // Cifra corta de la tarjeta de Fuentes ("312 juegos").
  countLabel: string;
};

export type ActiveSourcesState = {
  loading: boolean;
  views: ActiveSourceView[];
  // Resumen de Juegos para las secciones de Inicio que lo consumen directo
  // (stat band y actividad), evitando una segunda petición del hook.
  gamesSummary: GamesSummary | null;
};

function isLive(state: string | undefined): boolean {
  return state === "fresh" || state === "syncing";
}

function fmt(n: number): string {
  return Math.round(n).toLocaleString("es-ES");
}

export function useActiveSources(): ActiveSourcesState {
  const games = useGamesSource();
  const music = useMusicSource();
  const film = useFilmSource();
  const anime = useAnimeSource();
  const books = useBooksSource();

  const gamesSummary = games.source?.summary ?? null;
  const musicSummary = music.source?.summary ?? null;
  const filmSummary = film.source?.summary ?? null;
  const animeSummary = anime.source?.summary ?? null;
  const booksSummary = books.source?.summary ?? null;

  const views: ActiveSourceView[] = [
    {
      slug: "games",
      name: "Juegos",
      initial: "J",
      accent: "#3b82c4",
      provider: "Steam",
      modeLabel: "API",
      live: isLive(games.source?.state),
      syncing: games.source?.state === "syncing",
      heroValue: gamesSummary?.hours ?? 0,
      heroLabel: "horas jugadas",
      countLabel: `${fmt(gamesSummary?.games ?? 0)} juegos`,
    },
    {
      slug: "music",
      name: "Música",
      initial: "M",
      accent: "#d8543f",
      provider: "ListenBrainz",
      modeLabel: "API",
      live: isLive(music.source?.state),
      syncing: music.source?.state === "syncing",
      heroValue: musicSummary?.scrobbles_total ?? 0,
      heroLabel: "escuchas",
      countLabel: `${fmt(musicSummary?.scrobbles_total ?? 0)} escuchas`,
    },
    {
      slug: "film",
      name: "Cine y TV",
      initial: "C",
      accent: "#8b5cf6",
      provider: "Trakt",
      modeLabel: "API",
      live: isLive(film.source?.state),
      syncing: film.source?.state === "syncing",
      heroValue: filmSummary?.hours ?? 0,
      heroLabel: "horas vistas",
      countLabel: `${fmt(
        (filmSummary?.movies_watched ?? 0) + (filmSummary?.shows_watched ?? 0),
      )} títulos`,
    },
    {
      slug: "anime",
      name: "Anime y manga",
      initial: "A",
      accent: "#e0883c",
      provider: "AniList",
      modeLabel: "API",
      live: isLive(anime.source?.state),
      syncing: anime.source?.state === "syncing",
      heroValue: animeSummary?.episodes_watched ?? 0,
      heroLabel: "episodios vistos",
      countLabel: `${fmt(
        (animeSummary?.anime_watched ?? 0) + (animeSummary?.manga_read ?? 0),
      )} títulos`,
    },
    {
      slug: "books",
      name: "Libros",
      initial: "L",
      accent: "#2f9e6b",
      provider: "Goodreads",
      modeLabel: "Import",
      live: isLive(books.source?.state),
      syncing: books.source?.state === "syncing",
      heroValue: booksSummary?.books_read ?? 0,
      heroLabel: "libros leídos",
      countLabel: `${fmt(booksSummary?.books_read ?? 0)} leídos`,
    },
  ];

  const loading =
    games.loading || music.loading || film.loading || anime.loading || books.loading;
  return { loading, views, gamesSummary };
}
