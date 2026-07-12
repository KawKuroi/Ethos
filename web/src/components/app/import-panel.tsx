"use client";

import { useRef, useState } from "react";
import { ApiError, importFile, type ImportResult } from "@/lib/api";

// Botón de subida del import genérico: el usuario sube su export y el backend
// detecta el proveedor por la firma del archivo (D49/D62). La guía paso a
// paso por proveedor vive en el catálogo (providers.ts) y la muestra el
// ConnectHub.

export function ImportPanel({
  className,
  accept = ".csv,.json,text/csv,application/json",
  onImported,
}: {
  className?: string;
  accept?: string;
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
        accept={accept}
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
    </div>
  );
}
