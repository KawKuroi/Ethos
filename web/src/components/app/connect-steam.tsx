"use client";

import { useState } from "react";
import { getSteamLoginUrl } from "@/lib/api";

// Botón que arranca la conexión de Steam por OpenID: pide la URL al API y
// manda el navegador a Steam. Steam vuelve a /steam/return (página fuera de
// la shell de /app: se muestra a pantalla completa mientras verifica).
export function ConnectSteamButton({
  className,
  label = "Conectar Steam →",
}: {
  className?: string;
  label?: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    if (loading) return;
    setError(null);
    setLoading(true);
    try {
      const returnTo = `${window.location.origin}/steam/return`;
      const url = await getSteamLoginUrl(returnTo);
      window.location.href = url;
    } catch {
      setError("No se pudo iniciar la conexión con Steam. Inténtalo de nuevo.");
      setLoading(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className={className}
        onClick={start}
        disabled={loading}
      >
        {loading ? "Redirigiendo…" : label}
      </button>
      {error && (
        <span role="alert" style={{ color: "var(--error)", fontSize: "12.5px" }}>
          {error}
        </span>
      )}
    </>
  );
}
