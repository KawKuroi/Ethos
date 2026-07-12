"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { downloadContext, getContextText } from "@/lib/api";
import styles from "./category.module.css";

// Metadatos del historial del contexto (D60): cuánto del límite se usa.
type HistoryMeta = {
  limit: number;
  total: number;
  included: number;
  usage_pct: number;
  truncated: boolean;
};

function parseHistoryMeta(text: string): HistoryMeta | null {
  try {
    const history = (JSON.parse(text) as { history?: Partial<HistoryMeta> }).history;
    if (!history || typeof history.limit !== "number") return null;
    return {
      limit: history.limit,
      total: history.total ?? 0,
      included: history.included ?? 0,
      usage_pct: history.usage_pct ?? 0,
      truncated: history.truncated ?? false,
    };
  } catch {
    return null;
  }
}

// Modal "Descargar contexto" compartido por los detalles de categoría:
// vista previa del JSON real del backend, copiar y descargar
// `<slug>.context.json`. Se monta en un portal sobre <body>:
// `.eth-screen` conserva un transform (animación de entrada) que convertiría
// a la pantalla en el contenedor del `position: fixed` y el modal se
// centraría en el contenido, no en el viewport.
export function ContextDownloadModal({
  slug,
  onClose,
}: {
  slug: string;
  onClose: () => void;
}) {
  const [json, setJson] = useState<string | null>(null);
  const [meta, setMeta] = useState<HistoryMeta | null>(null);
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  useEffect(() => {
    let active = true;
    getContextText(slug)
      .then((text) => {
        if (!active) return;
        setJson(text);
        setMeta(parseHistoryMeta(text));
      })
      .catch(() => active && setJson("// No se pudo cargar el contexto."));
    return () => {
      active = false;
    };
  }, [slug]);

  const code = json ?? "Cargando…";
  const n = (value: number) => value.toLocaleString("es-ES");

  async function copy() {
    try {
      await navigator.clipboard?.writeText(code);
    } catch {
      /* el efímero confirma igual */
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  async function download() {
    await downloadContext(slug);
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 1600);
  }

  return createPortal(
    <div
      className={styles.overlay}
      role="dialog"
      aria-modal="true"
      aria-label="Descargar contexto"
      onClick={onClose}
    >
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHead}>
          <div className={styles.modalTitle}>Descargar contexto</div>
          <button type="button" className={styles.modalClose} onClick={onClose} aria-label="Cerrar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 6l12 12M18 6 6 18" strokeLinecap="round" />
            </svg>
          </button>
        </div>
        <div className={styles.modalBody}>
          <div className={styles.tabsRow}>
            <span className={styles.tabsLabel}>Vista previa</span>
          </div>
          {meta && (
            <div className={`${styles.limitRow} ${meta.truncated ? styles.limitRowWarn : ""}`}>
              <div className={styles.limitBar} role="presentation">
                <div
                  className={styles.limitFill}
                  style={{ width: `${Math.min(100, meta.usage_pct)}%` }}
                />
              </div>
              <span className={styles.limitText}>
                {meta.truncated
                  ? `Límite alcanzado: el historial incluye las ${n(meta.included)} entradas más recientes de ${n(meta.total)}`
                  : `Historial completo: ${n(meta.total)} entradas · ${meta.usage_pct} % del límite (${n(meta.limit)})`}
              </span>
            </div>
          )}
          <pre className={styles.code}>{code}</pre>
          <div className={styles.modalActions}>
            <button type="button" className={styles.btnGhost} onClick={copy}>
              {copied ? "Copiado ✓" : "Copiar"}
            </button>
            <button type="button" className={styles.btnPrimary} onClick={download}>
              {downloaded ? "Descargado ✓" : "↓ Descargar archivo"}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
