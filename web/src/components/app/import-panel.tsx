"use client";

import { useRef, useState } from "react";
import { ApiError, importFile, type ImportResult } from "@/lib/api";

// Panel de import genérico: el usuario sube su export y el backend detecta el
// proveedor por la firma del archivo (D49). Incluye la guía por proveedor
// (v1: Goodreads); añadir una guía es añadir una entrada a IMPORT_GUIDES.

export type ImportGuide = {
  provider: string;
  steps: string[];
};

export const IMPORT_GUIDES: ImportGuide[] = [
  {
    provider: "Goodreads",
    steps: [
      "Entra en Goodreads y abre My Books.",
      "En Tools (columna izquierda), elige Import and export → Export Library.",
      "Espera el enlace de descarga y guarda el archivo CSV.",
      "Súbelo aquí; detectamos el formato automáticamente.",
    ],
  },
];

export function ImportPanel({
  className,
  onImported,
}: {
  className?: string;
  onImported: (result: ImportResult) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setError(null);
    setLoading(true);
    try {
      const text = await file.text();
      const result = await importFile(text);
      onImported(result);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "No se pudo subir el archivo. Inténtalo de nuevo.",
      );
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "14px", alignItems: "center" }}>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        aria-label="Archivo de export"
        style={{ display: "none" }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
      <button
        type="button"
        className={className}
        disabled={loading}
        onClick={() => inputRef.current?.click()}
      >
        {loading ? "Importando…" : "↑ Subir export"}
      </button>
      {error && (
        <span role="alert" style={{ color: "var(--error)", fontSize: "12.5px", maxWidth: "420px" }}>
          {error}
        </span>
      )}
      {IMPORT_GUIDES.map((guide) => (
        <ol
          key={guide.provider}
          aria-label={`Cómo conseguir tu export de ${guide.provider}`}
          style={{
            margin: 0,
            paddingLeft: "18px",
            maxWidth: "420px",
            textAlign: "left",
            color: "var(--soft)",
            fontSize: "12.5px",
            lineHeight: 1.6,
          }}
        >
          {guide.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      ))}
    </div>
  );
}
