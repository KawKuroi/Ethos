"use client";

import { useState } from "react";

// Alta genérica de una fuente por username público: las fuentes que se leen
// sin OAuth ni contraseña (ListenBrainz D37, Trakt D41, AniList D45) solo
// necesitan un input. Al enviar, el backend guarda el username cifrado y
// encola el primer refresco en segundo plano.
export function ConnectUsernameForm({
  className,
  placeholder,
  ariaLabel,
  errorText,
  connect,
  onConnected,
}: {
  className?: string;
  placeholder: string;
  ariaLabel: string;
  errorText: string;
  connect: (userName: string) => Promise<void>;
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
      await connect(name);
      onConnected();
    } catch {
      setError(errorText);
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
          placeholder={placeholder}
          aria-label={ariaLabel}
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
