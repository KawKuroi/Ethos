"use client";

import { useCallback, useEffect, useState } from "react";
import { getGamesSource, type GamesSource } from "@/lib/api";

export type GamesSourceState = {
  loading: boolean;
  source: GamesSource | null;
  error: boolean;
  reload: () => void;
};

// Carga el estado + resumen de la fuente de juegos del usuario. Compartido por
// Inicio, Fuentes y el Detalle de Juegos.
export function useGamesSource(): GamesSourceState {
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState<GamesSource | null>(null);
  const [error, setError] = useState(false);
  const [tick, setTick] = useState(0);

  // El reset de loading/error va en el handler (no en el efecto) para no
  // disparar setState síncrono dentro del efecto.
  const reload = useCallback(() => {
    setLoading(true);
    setError(false);
    setTick((t) => t + 1);
  }, []);

  useEffect(() => {
    let active = true;
    getGamesSource()
      .then((data) => {
        if (!active) return;
        setSource(data);
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setError(true);
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [tick]);

  return { loading, source, error, reload };
}
