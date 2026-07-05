"use client";

import { getGamesSource, type GamesSource } from "@/lib/api";
import { useSource } from "@/lib/use-source";

export type GamesSourceState = {
  loading: boolean;
  source: GamesSource | null;
  error: boolean;
  reload: () => void;
};

// Carga el estado + resumen de la fuente de juegos del usuario. Compartido por
// Inicio, Fuentes y el Detalle de Juegos.
export function useGamesSource(): GamesSourceState {
  const { loading, data, error, reload } = useSource(getGamesSource);
  return { loading, source: data, error, reload };
}
