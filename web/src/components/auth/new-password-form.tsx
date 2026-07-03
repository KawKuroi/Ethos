"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getBrowserClient } from "@/lib/supabase/client";
import styles from "./auth.module.css";

export function NewPasswordForm() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (loading) return;
    setError(null);
    if (password.length < 8) {
      setError("La contraseña necesita al menos 8 caracteres.");
      return;
    }
    if (password !== confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setLoading(true);
    try {
      const { error: authError } = await getBrowserClient().auth.updateUser({
        password,
      });
      if (authError) {
        setError(
          "No pudimos actualizar la contraseña. Pide un enlace nuevo e inténtalo otra vez.",
        );
        setLoading(false);
        return;
      }
      router.push("/app");
    } catch {
      setError("No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.");
      setLoading(false);
    }
  }

  return (
    <div className={styles.card}>
      <h2 className={styles.heading}>Nueva contraseña</h2>
      <p className={styles.sub}>Elige una contraseña para tu cuenta.</p>

      <form className={styles.form} onSubmit={onSubmit} noValidate>
        <label className={styles.field}>
          <span className={styles.label}>Contraseña</span>
          <span className={styles.pwWrap}>
            <input
              className={`${styles.input} ${styles.pwInput}`}
              type={showPw ? "text" : "password"}
              placeholder="Mínimo 8 caracteres"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
            <button
              type="button"
              className={styles.pwToggle}
              onClick={() => setShowPw((v) => !v)}
              title="Mostrar u ocultar contraseña"
              aria-label="Mostrar u ocultar contraseña"
            >
              {showPw ? (
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M3 3l18 18" strokeLinecap="round" />
                  <path d="M10.6 5.1A9.9 9.9 0 0 1 12 5c5.5 0 9 5.5 9 7-.3 1-1.3 2.5-2.8 3.8M6.2 6.3C3.9 7.8 3 10.2 3 12c0 1.2 3.5 7 9 7 1.6 0 3-.5 4.2-1.2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M9.8 9.9a3 3 0 0 0 4.2 4.2" strokeLinecap="round" />
                </svg>
              ) : (
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M3 12s3.5-7 9-7 9 7 9 7-3.5 7-9 7-9-7-9-7z" strokeLinejoin="round" />
                  <circle cx="12" cy="12" r="2.6" />
                </svg>
              )}
            </button>
          </span>
        </label>

        <label className={styles.field}>
          <span className={styles.label}>Repetir contraseña</span>
          <input
            className={styles.input}
            type={showPw ? "text" : "password"}
            placeholder="Repite la contraseña"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
          />
        </label>

        {error && <p className={styles.error}>{error}</p>}

        <button type="submit" className={styles.submit} disabled={loading}>
          {loading ? (
            <span className={styles.spinner} aria-hidden="true" />
          ) : (
            "Guardar contraseña"
          )}
        </button>
      </form>
    </div>
  );
}
