"use client";

import { getBooksSource, type BooksSource } from "@/lib/api";
import { useSource } from "@/lib/use-source";

export type BooksSourceState = {
  loading: boolean;
  source: BooksSource | null;
  error: boolean;
  reload: () => void;
  silentReload: () => void;
};

// Carga el estado + resumen de la fuente de Libros del usuario.
export function useBooksSource(): BooksSourceState {
  const { loading, data, error, reload, silentReload } = useSource(getBooksSource);
  return { loading, source: data, error, reload, silentReload };
}
