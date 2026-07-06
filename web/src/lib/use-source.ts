"use client";

import { useCallback, useEffect, useState } from "react";

// Marca en sessionStorage que la conexión de Steam acaba de completarse en
// /steam/return: el Detalle de Juegos la lee al montar para mostrar la
// sincronización aunque el estado del backend aún no sea "syncing".
export const JUST_CONNECTED_GAMES = "ethos_just_connected_games";

export type SourceState<T> = {
  loading: boolean;
  data: T | null;
  error: boolean;
  reload: () => void;
  // Recarga sin pasar por el estado "cargando": para el polling de las vistas
  // de sincronización (los datos se sustituyen cuando llegan, sin parpadeo).
  silentReload: () => void;
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

  const silentReload = useCallback(() => {
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

  return { loading, data, error, reload, silentReload };
}

// Recarga silenciosa periódica mientras `active` (p. ej. fuente sincronizando):
// la pantalla pasa sola de "sincronizando…" a los datos, sin recargar a mano.
export function useAutoReload(
  active: boolean,
  silentReload: () => void,
  intervalMs = 4000,
): void {
  useEffect(() => {
    if (!active) return;
    const id = setInterval(silentReload, intervalMs);
    return () => clearInterval(id);
  }, [active, silentReload, intervalMs]);
}
