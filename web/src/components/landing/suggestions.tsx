"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { submitFeedback } from "@/lib/api";
import styles from "./landing.module.css";

// Formulario de sugerencias con envío real (persistencia + aviso, D52).
export function Suggestions() {
  const [sent, setSent] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (sending || sent) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const message = String(data.get("suggestion") ?? "").trim();
    if (!message) {
      setError("Escribe tu sugerencia antes de enviarla.");
      return;
    }
    setSending(true);
    setError("");
    try {
      await submitFeedback({
        message,
        name: String(data.get("name") ?? "").trim() || null,
        email: String(data.get("email") ?? "").trim() || null,
      });
      setSent(true);
      form.reset();
      setTimeout(() => setSent(false), 1600);
    } catch {
      setError("No se pudo enviar. Reinténtalo.");
    } finally {
      setSending(false);
    }
  };

  return (
    <section className={`eth-reveal ${styles.sugSection}`}>
      <div>
        <div className={styles.sugEyebrow}>Sugerencias</div>
        <h2 className={styles.sugTitle}>
          ¿Ideas o algo que falta? Escríbeme.
        </h2>
        <p className={styles.sugText}>
          Esto se construye en abierto. Cuéntame qué categoría o proveedor te
          gustaría ver — o abre un issue en GitHub.
        </p>
      </div>
      <form className={styles.sugForm} onSubmit={handleSubmit}>
        <input
          className={styles.input}
          placeholder="Tu nombre"
          name="name"
          aria-label="Tu nombre"
        />
        <input
          className={styles.input}
          placeholder="Tu correo"
          name="email"
          type="email"
          aria-label="Tu correo"
        />
        <textarea
          className={`${styles.input} ${styles.textarea}`}
          placeholder="Tu sugerencia"
          name="suggestion"
          rows={3}
          aria-label="Tu sugerencia"
        />
        <button type="submit" className={styles.sendBtn} disabled={sending}>
          {sent ? "Enviado ✓" : sending ? "Enviando…" : "Enviar sugerencia"}
        </button>
        {error && (
          <span className={styles.sugError} role="alert">
            {error}
          </span>
        )}
      </form>
    </section>
  );
}
