"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import styles from "./landing.module.css";

// Formulario de sugerencias. El envío real (persistencia) llega en Fase 4;
// mientras, usa el efímero "Enviado ✓" del design system.
export function Suggestions() {
  const [sent, setSent] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSent(true);
    event.currentTarget.reset();
    setTimeout(() => setSent(false), 1600);
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
        <button type="submit" className={styles.sendBtn}>
          {sent ? "Enviado ✓" : "Enviar sugerencia"}
        </button>
      </form>
    </section>
  );
}
