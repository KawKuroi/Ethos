"use client";

import { getMusicSource, type MusicSource } from "@/lib/api";
import { useSource } from "@/lib/use-source";

export type MusicSourceState = {
  loading: boolean;
  source: MusicSource | null;
  error: boolean;
  reload: () => void;
};

// Carga el estado + resumen de la fuente de música del usuario. Compartido por
// Inicio, Fuentes y el Detalle de Música.
export function useMusicSource(): MusicSourceState {
  const { loading, data, error, reload } = useSource(getMusicSource);
  return { loading, source: data, error, reload };
}
