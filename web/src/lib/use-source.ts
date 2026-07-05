"use client";

import { useCallback, useEffect, useState } from "react";

export type SourceState<T> = {
  loading: boolean;
  data: T | null;
  error: boolean;
  reload: () => void;
};

// Carga perezosa del estado de una fuente del usuario con recarga bajo demanda.
// Parametrizado por el cargador (`load`) para compartirlo entre categorías.
// `load` debe ser una referencia estable (una función de módulo), no un inline.
export function useSource<T>(load: () => Promise<T>): SourceState<T> {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<T | null>(null);
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
    load()
      .then((result) => {
        if (!active) return;
        setData(result);
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
  }, [load, tick]);

  return { loading, data, error, reload };
}
