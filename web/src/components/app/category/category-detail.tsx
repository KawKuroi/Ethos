"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { CSSProperties } from "react";
import { NotifyForm } from "@/components/notify-form";
import { getBrowserClient } from "@/lib/supabase/client";
import type { CategoryDetailData } from "./data";
import { contextJson, contextMcp } from "./context";
import { sparkPoints } from "./sparkline";
import styles from "./category.module.css";

function accentVar(accent: string): CSSProperties {
  return { "--catAccent": accent } as CSSProperties;
}

const HEALTH_CLASS: Record<NonNullable<CategoryDetailData["health"]>["state"], string> = {
  ok: styles.healthOk,
  warn: styles.healthWarn,
  error: styles.healthError,
};

function DownloadModal({
  category,
  onClose,
}: {
  category: CategoryDetailData;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<"json" | "mcp">("json");
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const json = contextJson(category);
  const mcp = contextMcp(category);
  const code = tab === "mcp" ? mcp : json;

  async function copy() {
    try {
      await navigator.clipboard?.writeText(code);
    } catch {
      // El portapapeles puede no estar disponible; el efímero igual confirma.
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  function download() {
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${category.slug}.context.json`;
    a.click();
    URL.revokeObjectURL(url);
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
          <button
            type="button"
            className={styles.modalClose}
            onClick={onClose}
            aria-label="Cerrar"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 6l12 12M18 6 6 18" strokeLinecap="round" />
            </svg>
          </button>
        </div>
        <div className={styles.modalBody}>
          <div className={styles.tabsRow}>
            <span className={styles.tabsLabel}>Vista previa</span>
            <div className={styles.tabs}>
              <button
                type="button"
                className={`${styles.tab} ${tab === "json" ? styles.tabActive : ""}`}
                onClick={() => setTab("json")}
              >
                JSON
              </button>
              <button
                type="button"
                className={`${styles.tab} ${tab === "mcp" ? styles.tabActive : ""}`}
                onClick={() => setTab("mcp")}
              >
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

// Pantalla de categoría en desarrollo con aviso (D50). Prellena el correo con
// el de la sesión para que el usuario del panel solo confirme.
function SoonScreen({ category }: { category: CategoryDetailData }) {
  const [email, setEmail] = useState("");

  useEffect(() => {
    let active = true;
    try {
      getBrowserClient()
        .auth.getUser()
        .then(({ data }) => {
          if (active && data.user?.email) setEmail(data.user.email);
        })
        .catch(() => {
          // Sin sesión legible: el usuario escribe el correo a mano.
        });
    } catch {
      // Cliente de Supabase sin configurar (SSR/tests): sin prellenado.
    }
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="eth-screen">
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>
      <div className={styles.soon}>
        <span className={styles.soonBadge}>
          <span className={styles.soonBadgeDot} />
          {category.soonEta}
        </span>
        <div className={styles.soonTitle}>Esta categoría está en desarrollo</div>
        <p className={styles.soonNote}>
          {category.soonNote} Aún no puedes conectar{" "}
          <strong style={{ color: "var(--ink)", fontWeight: 600 }}>
            {category.provider}
          </strong>
          , pero ya la estamos preparando.
        </p>
        <div className={styles.soonNotify}>
          <NotifyForm category={category.slug} accent={category.accent} defaultEmail={email} />
        </div>
      </div>
    </div>
  );
}

export function CategoryDetail({ category }: { category: CategoryDetailData }) {
  const [refreshing, setRefreshing] = useState(false);
  const [fresh, setFresh] = useState(category.freshLabel ?? "");
  const [modalOpen, setModalOpen] = useState(false);

  function refresh() {
    if (refreshing) return;
    setRefreshing(true);
    setFresh("sincronizando…");
    setTimeout(() => {
      setRefreshing(false);
      setFresh("hace unos seg");
    }, 1400);
  }

  if (category.state === "soon") {
    return <SoonScreen category={category} />;
  }

  const stats = category.stats ?? [];
  const top = category.top ?? [];
  const recent = category.recent ?? [];
  const tags = category.tags ?? [];
  const health = category.health;

  return (
    <div className="eth-screen" style={accentVar(category.accent)}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>

      <div className={styles.header}>
        <span className={styles.headerIcon}>{category.name.charAt(0)}</span>
        <div className={styles.headerBody}>
          <h2 className={styles.headerName}>{category.name}</h2>
          <div className={styles.headerBlurb}>{category.blurb}</div>
        </div>
        <div className={styles.headerActions}>
          <button type="button" className={styles.btnGhost} onClick={refresh}>
            {refreshing ? <span className={styles.spin} /> : null}
            {refreshing ? "Sincronizando…" : "Refrescar"}
          </button>
          <button
            type="button"
            className={styles.btnPrimary}
            onClick={() => setModalOpen(true)}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 3v11m0 0 4-4m-4 4-4-4" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M5 19h14" strokeLinecap="round" />
            </svg>
            Descargar contexto
          </button>
        </div>
      </div>

      {health && (
        <div className={styles.strip}>
          <span className={styles.stripItem}>
            <span className={`${styles.healthDot} ${HEALTH_CLASS[health.state]}`} />
            <span className={styles.stripStrong}>{health.label}</span>
          </span>
          <span className={styles.stripSep} />
          <span className={styles.stripItem}>
            Proveedor
            <span className={styles.provider}>{category.provider}</span>
          </span>
          <span className={styles.stripItem}>
            Modo <span className={styles.stripStrong}>{category.modeLabel}</span>
          </span>
          <span className={styles.stripGrow} />
          <span className={styles.stripItem}>Actualizado {fresh}</span>
        </div>
      )}

      <div className={styles.statBand}>
        <div className={styles.statHero}>
          <div>
            <div className={styles.heroValue}>{category.hero?.value}</div>
            <div className={styles.heroLabel}>{category.hero?.label}</div>
          </div>
          {category.spark && (
            <svg
              width="150"
              height="44"
              viewBox="0 0 100 26"
              preserveAspectRatio="none"
              className={styles.spark}
              aria-hidden="true"
            >
              <polyline
                points={sparkPoints(category.spark)}
                fill="none"
                stroke={category.accent}
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
              />
            </svg>
          )}
        </div>
        <div className={styles.statGrid}>
          {stats.map((stat) => (
            <div key={stat.label} className={styles.statCell}>
              <div className={styles.statValue}>{stat.value}</div>
              <div className={styles.statLabel}>{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <div className={styles.eyebrow}>{category.topTitle}</div>
        {top.map((item) => (
          <div key={item.rank} className={styles.topRow}>
            <div className={styles.rank}>{item.rank}</div>
            <div className={styles.topBody}>
              <div className={styles.topHead}>
                <span className={styles.topName}>{item.name}</span>
                <span className={styles.topValue}>{item.value}</span>
              </div>
              <div className={styles.topSub}>{item.sub}</div>
              <div className={styles.topBar}>
                <div className={styles.topBarFill} style={{ width: `${item.bar}%` }} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.section}>
        <div className={styles.eyebrow}>{category.recentTitle}</div>
        {recent.map((item) => (
          <div key={item.name} className={styles.recentRow}>
            <span className={styles.recentDot} />
            <div className={styles.recentBody}>
              <div className={styles.recentName}>{item.name}</div>
              <div className={styles.recentSub}>{item.sub}</div>
            </div>
            <span className={styles.recentTime}>{item.time}</span>
          </div>
        ))}
      </div>

      <div className={styles.section}>
        <div className={styles.eyebrow}>{category.tagsTitle}</div>
        <div className={styles.tags}>
          {tags.map((tag) => (
            <span key={tag} className={styles.tag}>
              {tag}
            </span>
          ))}
        </div>
      </div>

      {modalOpen && (
        <DownloadModal category={category} onClose={() => setModalOpen(false)} />
      )}
    </div>
  );
}
