"use client";

import { useEffect, useState } from "react";
import { downloadContext, getContextText } from "@/lib/api";
import styles from "./category.module.css";

// Modal "Descargar contexto" compartido por los detalles de categoría:
// vista previa JSON (real, del backend) / MCP (ilustrativa), copiar y
// descargar `<slug>.context.json`.
export function ContextDownloadModal({
  slug,
  mcpPreview,
  onClose,
}: {
  slug: string;
  mcpPreview: string;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<"json" | "mcp">("json");
  const [json, setJson] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  useEffect(() => {
    let active = true;
    getContextText(slug)
      .then((text) => active && setJson(text))
      .catch(() => active && setJson("// No se pudo cargar el contexto."));
    return () => {
      active = false;
    };
  }, [slug]);

  const code = tab === "mcp" ? mcpPreview : (json ?? "Cargando…");

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

  return (
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
            <div className={styles.tabs}>
              <button type="button" className={`${styles.tab} ${tab === "json" ? styles.tabActive : ""}`} onClick={() => setTab("json")}>
                JSON
              </button>
              <button type="button" className={`${styles.tab} ${tab === "mcp" ? styles.tabActive : ""}`} onClick={() => setTab("mcp")}>
                MCP
              </button>
            </div>
          </div>
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
    </div>
  );
}
