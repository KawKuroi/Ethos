"use client";

import { useState, type CSSProperties, type FormEvent } from "react";
import { ApiError, registerCategoryInterest } from "@/lib/api";
import styles from "./notify-form.module.css";

// Formulario "Avísame cuando esté lista" para una categoría en desarrollo
// (D50). Compartido por la landing (visitante anónimo) y el panel (usuario con
// sesión, correo prellenado). Persiste el interés vía /category-interest.
export function NotifyForm({
  category,
  accent,
  defaultEmail = "",
}: {
  category: string;
  accent?: string;
  defaultEmail?: string;
}) {
  const [email, setEmail] = useState(defaultEmail);
  const [state, setState] = useState<"idle" | "sending" | "done" | "error">("idle");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (state === "sending" || state === "done") return;
    setState("sending");
    setError("");
    try {
      await registerCategoryInterest(category, email.trim());
      setState("done");
    } catch (err) {
      setState("error");
      setError(err instanceof ApiError ? err.message : "No se pudo registrar. Reinténtalo.");
    }
  }

  const accentStyle = accent ? ({ "--notifyAccent": accent } as CSSProperties) : undefined;

  if (state === "done") {
    return (
      <p className={styles.done} style={accentStyle}>
        Te avisaremos en <strong>{email}</strong> cuando esté lista.
      </p>
    );
  }

  return (
    <form className={styles.form} onSubmit={submit} style={accentStyle}>
      <input
        type="email"
        required
        className={styles.input}
        placeholder="tu@correo.com"
        aria-label="Correo para el aviso"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={state === "sending"}
      />
      <button type="submit" className={styles.button} disabled={state === "sending"}>
        {state === "sending" ? "Enviando…" : "Avísame"}
      </button>
      {state === "error" && (
        <span className={styles.error} role="alert">
          {error}
        </span>
      )}
    </form>
  );
}
