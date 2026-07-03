"use client";

import { useState } from "react";
import { FAQS } from "./data";
import styles from "./help.module.css";

export function Help() {
  const [open, setOpen] = useState(0);
  const [text, setText] = useState("");
  const [sent, setSent] = useState(false);

  function send() {
    if (sent || text.trim().length === 0) return;
    // Envío real de sugerencias: Fase 4 (persistencia + notificación).
    setSent(true);
    setText("");
    setTimeout(() => setSent(false), 1800);
  }

  return (
    <div className="eth-screen">
      <div className={styles.hero}>
        <div className={styles.eyebrow}>Ayuda · cómo funciona</div>
        <h2 className={styles.heroTitle}>
          Tu gusto es tuyo. Ethos solo lo ordena y te deja decidir quién lo lee.
        </h2>
      </div>

      <div className={styles.grid}>
        <div>
          <div className={styles.faqHead}>
            <div className={styles.eyebrow}>Preguntas frecuentes</div>
            <div className={styles.faqCount}>{FAQS.length}</div>
          </div>
          {FAQS.map((faq, index) => {
            const isOpen = open === index;
            return (
              <div key={faq.q} className={styles.faqItem}>
                <button
                  type="button"
                  className={styles.faqButton}
                  onClick={() => setOpen(isOpen ? -1 : index)}
                  aria-expanded={isOpen}
                >
                  <span className={styles.faqNum}>
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className={styles.faqQ}>{faq.q}</span>
                  <span
                    className={`${styles.faqChevron} ${isOpen ? styles.faqChevronOpen : ""}`}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </span>
                </button>
                {isOpen && <div className={styles.faqAnswer}>{faq.a}</div>}
              </div>
            );
          })}
        </div>

        <div className={styles.rail}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>¿Echas algo en falta?</div>
            <div className={styles.cardSub}>Una línea basta. Lo leemos todo.</div>
            <textarea
              className={styles.textarea}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Cuéntanos qué te gustaría ver en Ethos…"
              aria-label="Tu sugerencia"
            />
            <div className={styles.suggestFoot}>
              <span className={styles.anon}>
                <svg width="12" height="12" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6">
                  <rect x="3" y="8" width="12" height="8" rx="1.5" />
                  <path d="M6 8V6a3 3 0 0 1 6 0v2" strokeLinecap="round" />
                </svg>
                Anónimo
              </span>
              <button
                type="button"
                className={styles.sendBtn}
                onClick={send}
                disabled={sent}
              >
                {sent ? "Enviado ✓" : "Enviar →"}
              </button>
            </div>
          </div>

          <div className={styles.contact}>
            <span className={styles.contactIcon}>
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <path d="m3 7 9 6 9-6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <div className={styles.contactBody}>
              <div className={styles.contactTitle}>¿Algo más personal?</div>
              <div className={styles.contactSub}>Escríbenos y te respondemos.</div>
            </div>
            <a href="mailto:hola@ethos.app" className={styles.contactBtn}>
              Escribir
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
