"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { approveOAuth, NotAuthenticatedError } from "@/lib/api";
import { getBrowserClient } from "@/lib/supabase/client";
import styles from "./consent.module.css";

type Phase = "loading" | "ready" | "noauth" | "working" | "redirecting" | "error";

// Página de consentimiento del flujo OAuth del MCP (D56): el authorization
// endpoint del API redirige aquí; el usuario (con su sesión de Supabase)
// aprueba o deniega y el navegador vuelve al cliente con el code.
export function OAuthConsent() {
  const params = useSearchParams();
  const clientId = params.get("client_id") ?? "";
  const clientName = params.get("client_name") || "Tu cliente MCP";
  const redirectUri = params.get("redirect_uri") ?? "";
  const codeChallenge = params.get("code_challenge") ?? "";
  const state = params.get("state");
  const scope = params.get("scope");

  const [phase, setPhase] = useState<Phase>("loading");
  const valid = Boolean(clientId && redirectUri && codeChallenge);

  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        const { data } = await getBrowserClient().auth.getSession();
        if (active) setPhase(data.session ? "ready" : "noauth");
      } catch {
        // Cliente de Supabase sin configurar o sesión ilegible.
        if (active) setPhase("noauth");
      }
    };
    void check();
    return () => {
      active = false;
    };
  }, []);

  async function decide(approve: boolean) {
    if (phase === "working" || phase === "redirecting") return;
    setPhase("working");
    try {
      const redirectTo = await approveOAuth(
        {
          client_id: clientId,
          redirect_uri: redirectUri,
          code_challenge: codeChallenge,
          state,
          scope,
        },
        approve,
      );
      setPhase("redirecting");
      window.location.href = redirectTo;
    } catch (error) {
      setPhase(error instanceof NotAuthenticatedError ? "noauth" : "error");
    }
  }

  if (!valid) {
    return (
      <Shell>
        <div className={styles.title}>Solicitud inválida</div>
        <p className={styles.text}>
          Faltan parámetros del flujo OAuth. Vuelve a iniciar la conexión desde
          tu cliente MCP.
        </p>
      </Shell>
    );
  }

  if (phase === "loading") {
    return (
      <Shell>
        <p className={styles.text}>Comprobando tu sesión…</p>
      </Shell>
    );
  }

  if (phase === "noauth") {
    return (
      <Shell>
        <div className={styles.title}>Inicia sesión para continuar</div>
        <p className={styles.text}>
          Para autorizar a <strong>{clientName}</strong> necesitas tu sesión de
          Ethos. Inicia sesión y vuelve a intentar la conexión desde tu cliente.
        </p>
        <Link href="/auth" className={styles.primary}>
          Ir a iniciar sesión
        </Link>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className={styles.title}>Autorizar acceso</div>
      <p className={styles.text}>
        <strong>{clientName}</strong> quiere consultar tu perfil de gusto por
        MCP (lectura acotada por consulta). Podrás revocarlo generando un nuevo
        token en Conectar IA.
      </p>
      <div className={styles.scope}>
        <span className={styles.scopeChip}>{scope || "ethos:read"}</span>
      </div>
      {phase === "error" && (
        <p className={styles.error} role="alert">
          No se pudo completar la autorización. Reinténtalo.
        </p>
      )}
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.ghost}
          onClick={() => decide(false)}
          disabled={phase === "working" || phase === "redirecting"}
        >
          Denegar
        </button>
        <button
          type="button"
          className={styles.primary}
          onClick={() => decide(true)}
          disabled={phase === "working" || phase === "redirecting"}
        >
          {phase === "redirecting"
            ? "Redirigiendo…"
            : phase === "working"
              ? "Un momento…"
              : "Autorizar"}
        </button>
      </div>
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className={styles.wrap}>
      <div className={styles.card}>{children}</div>
    </main>
  );
}
