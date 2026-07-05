"use client";

import { useState } from "react";
import { connectListenBrainz } from "@/lib/api";

// Alta de la fuente de música: ListenBrainz se lee por username público (D37),
// así que basta un input (sin OpenID ni contraseña). Al enviar, el backend
// guarda el username cifrado y encola el primer refresco en segundo plano.
export function ConnectListenBrainzForm({
  className,
  onConnected,
}: {
  className?: string;
  onConnected: () => void;
}) {
  const [userName, setUserName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    const name = userName.trim();
    if (!name || loading) return;
    setError(null);
    setLoading(true);
    try {
      await connectListenBrainz(name);
      onConnected();
    } catch {
      setError(
        "No se pudo conectar. Revisa tu nombre de usuario de ListenBrainz e inténtalo de nuevo.",
      );
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "10px", alignItems: "center" }}>
      <div style={{ display: "flex", gap: "8px", width: "100%", maxWidth: "360px" }}>
        <input
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
          }}
          placeholder="Tu usuario de ListenBrainz"
          aria-label="Nombre de usuario de ListenBrainz"
          disabled={loading}
          style={{
            flex: 1,
            minWidth: 0,
            padding: "9px 12px",
            borderRadius: "var(--rs)",
            border: "1px solid var(--line)",
            background: "var(--surface)",
            color: "var(--ink)",
            fontSize: "13.5px",
          }}
        />
        <button
          type="button"
          className={className}
          onClick={submit}
          disabled={loading}
        >
          {loading ? "Conectando…" : "Conectar →"}
        </button>
      </div>
      {error && (
        <span role="alert" style={{ color: "var(--error)", fontSize: "12.5px" }}>
          {error}
        </span>
      )}
    </div>
  );
}
