"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { connectSteam } from "@/lib/api";
import { JUST_CONNECTED_GAMES } from "@/lib/use-source";

type Phase = "connecting" | "error";

// Retorno del login OpenID de Steam: recoge los parámetros `openid.*` de la URL,
// los postea al API (que los verifica contra Steam) y lleva a Juegos.
export default function SteamReturnPage() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("connecting");

  useEffect(() => {
    const params: Record<string, string> = {};
    new URLSearchParams(window.location.search).forEach((value, key) => {
      if (key.startsWith("openid.")) params[key] = value;
    });
    connectSteam(params)
      .then(() => {
        // Señal para que el Detalle de Juegos muestre la sincronización
        // (el primer refresco corre en segundo plano tras conectar).
        sessionStorage.setItem(JUST_CONNECTED_GAMES, "1");
        router.replace("/app/categoria/games");
      })
      .catch(() => setPhase("error"));
  }, [router]);

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "12px",
        padding: "40px 24px",
        textAlign: "center",
      }}
    >
      <h1 style={{ fontFamily: "var(--fd)", fontWeight: 700, fontSize: "24px", margin: 0 }}>
        {phase === "error" ? "No se pudo conectar Steam" : "Conectando tu cuenta de Steam…"}
      </h1>
      <p style={{ fontFamily: "var(--fb)", color: "var(--muted)", margin: 0, maxWidth: "420px" }}>
        {phase === "error"
          ? "El retorno de Steam no se pudo verificar. Vuelve a intentarlo desde Fuentes."
          : "Estamos verificando el retorno de Steam y preparando tu biblioteca."}
      </p>
      {phase === "error" && (
        <a
          href="/app/fuentes"
          style={{ fontFamily: "var(--fb)", fontWeight: 700, color: "var(--accent)" }}
        >
          ← Volver a Fuentes
        </a>
      )}
    </main>
  );
}
