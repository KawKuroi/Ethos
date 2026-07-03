"use client";

import { useState } from "react";
import Link from "next/link";
import { getBrowserClient } from "@/lib/supabase/client";
import styles from "./auth.module.css";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function RecoverForm() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (loading) return;
    setError(null);
    if (!EMAIL_RE.test(email)) {
      setError("Escribe un correo válido.");
      return;
    }
    setLoading(true);
    try {
      const { error: authError } = await getBrowserClient().auth.resetPasswordForEmail(
        email,
        { redirectTo: `${window.location.origin}/auth/callback?next=/auth/nueva-clave` },
      );
      if (authError) {
        setError("Algo salió mal. Inténtalo de nuevo.");
        setLoading(false);
        return;
      }
      setSent(true);
      setLoading(false);
    } catch {
      setError("No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.");
      setLoading(false);
    }
  }

  return (
    <div className={styles.card}>
      <h2 className={styles.heading}>Recuperar contraseña</h2>
      <p className={styles.sub}>
        Escribe tu correo y te enviaremos un enlace para elegir una nueva
        contraseña.
      </p>

      {sent ? (
        <p className={styles.ok}>
          Si existe una cuenta con ese correo, te enviamos un enlace para
          restablecer la contraseña.
        </p>
      ) : (
        <form className={styles.form} onSubmit={onSubmit} noValidate>
          <label className={styles.field}>
            <span className={styles.label}>Correo</span>
            <input
              className={styles.input}
              type="email"
              placeholder="tu@correo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" className={styles.submit} disabled={loading}>
            {loading ? (
              <span className={styles.spinner} aria-hidden="true" />
            ) : (
              "Enviar enlace"
            )}
          </button>
        </form>
      )}

      <div className={styles.switch}>
        <Link href="/auth" className={styles.back}>
          ← Volver a iniciar sesión
        </Link>
      </div>
    </div>
  );
}
