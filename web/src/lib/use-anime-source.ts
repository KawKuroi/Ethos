"use client";

import { getAnimeSource, type AnimeSource } from "@/lib/api";
import { useSource } from "@/lib/use-source";

export type AnimeSourceState = {
  loading: boolean;
  source: AnimeSource | null;
  error: boolean;
  reload: () => void;
  silentReload: () => void;
};

// Carga el estado + resumen de la fuente de Anime y manga del usuario.
export function useAnimeSource(): AnimeSourceState {
  const { loading, data, error, reload, silentReload } = useSource(getAnimeSource);
  return { loading, source: data, error, reload, silentReload };
}
