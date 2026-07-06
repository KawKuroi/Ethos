"use client";

import { getFilmSource, type FilmSource } from "@/lib/api";
import { useSource } from "@/lib/use-source";

export type FilmSourceState = {
  loading: boolean;
  source: FilmSource | null;
  error: boolean;
  reload: () => void;
  silentReload: () => void;
};

// Carga el estado + resumen de la fuente de Cine y TV del usuario. Compartido
// por Inicio, Fuentes y el Detalle de Cine y TV.
export function useFilmSource(): FilmSourceState {
  const { loading, data, error, reload, silentReload } = useSource(getFilmSource);
  return { loading, source: data, error, reload, silentReload };
}
