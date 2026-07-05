"use client";

import { useState } from "react";
import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import {
  refreshListenBrainz,
  type MusicSource,
  type MusicSummary,
} from "@/lib/api";
import { fmtInt as fmt, relativeTime } from "@/lib/format";
import { useMusicSource } from "@/lib/use-music-source";
import { ConnectListenBrainzForm } from "../connect-listenbrainz";
import { ContextDownloadModal } from "./context-modal";
import { CATEGORY_DETAIL } from "./data";
import styles from "./category.module.css";

const MUSIC = CATEGORY_DETAIL.music;

function accentVar(): CSSProperties {
  return { "--catAccent": MUSIC.accent } as CSSProperties;
}

function mcpPreview(): string {
  return [
    "// Tu IA descubre y llama la herramienta",
    'ethos.context({ tool: "music.*", ask: "más escuchadas este mes" })',
    "",
    "→ 200 OK · contexto acotado servido en vivo",
    "  { provider, summary, top_artists, top_tracks }",
  ].join("\n");
}

function Header({ actions }: { actions?: ReactNode }) {
  return (
    <div className={styles.header}>
      <span className={styles.headerIcon}>M</span>
      <div className={styles.headerBody}>
        <h2 className={styles.headerName}>Música</h2>
        <div className={styles.headerBlurb}>{MUSIC.blurb}</div>
      </div>
      {actions && <div className={styles.headerActions}>{actions}</div>}
    </div>
  );
}

function TopList({ title, entries }: { title: string; entries: MusicSummary["top_artists"] }) {
  if (entries.length === 0) return null;
  const max = entries[0]?.count || 1;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>{title}</div>
      {entries.map((entry, i) => (
        <div key={entry.name} className={styles.topRow}>
          <div className={styles.rank}>{i + 1}</div>
          <div className={styles.topBody}>
            <div className={styles.topHead}>
              <span className={styles.topName}>{entry.name}</span>
              <span className={styles.topValue}>
                {entry.count.toLocaleString("es-ES")} escuchas
              </span>
            </div>
            <div className={styles.topBar}>
              <div
                className={styles.topBarFill}
                style={{ width: `${Math.round((entry.count / max) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ConnectedView({
  source,
  summary,
  onRefresh,
}: {
  source: MusicSource;
  summary: MusicSummary;
  onRefresh: () => void;
}) {
  const [refreshing, setRefreshing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  async function refresh() {
    if (refreshing) return;
    setRefreshing(true);
    try {
      await refreshListenBrainz();
    } finally {
      setRefreshing(false);
      onRefresh();
    }
  }

  const stats = [
    { value: fmt(summary.scrobbles_window), label: `últimos ${summary.window_days} d` },
    { value: String(summary.top_artists.length), label: "artistas en tu top" },
    { value: String(summary.top_tracks.length), label: "canciones en tu top" },
  ];

  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>

      <Header
        actions={
          <>
            <button type="button" className={styles.btnGhost} onClick={refresh}>
              {refreshing ? <span className={styles.spin} /> : null}
              {refreshing ? "Sincronizando…" : "Refrescar"}
            </button>
            <button type="button" className={styles.btnPrimary} onClick={() => setModalOpen(true)}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 3v11m0 0 4-4m-4 4-4-4" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M5 19h14" strokeLinecap="round" />
              </svg>
              Descargar contexto
            </button>
          </>
        }
      />

      <div className={styles.strip}>
        <span className={styles.stripItem}>
          <span className={`${styles.healthDot} ${styles.healthOk}`} />
          <span className={styles.stripStrong}>Operativa</span>
        </span>
        <span className={styles.stripSep} />
        <span className={styles.stripItem}>
          Proveedor <span className={styles.provider}>ListenBrainz</span>
        </span>
        <span className={styles.stripItem}>
          Modo <span className={styles.stripStrong}>API · en vivo</span>
        </span>
        <span className={styles.stripGrow} />
        <span className={styles.stripItem}>Actualizado {relativeTime(source.synced_at)}</span>
      </div>

      <div className={styles.statBand}>
        <div className={styles.statHero}>
          <div>
            <div className={styles.heroValue}>{fmt(summary.scrobbles_total)}</div>
            <div className={styles.heroLabel}>escuchas registradas</div>
          </div>
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

      <TopList title={`Top artistas · últimos ${summary.window_days} días`} entries={summary.top_artists} />
      <TopList title={`Top canciones · últimos ${summary.window_days} días`} entries={summary.top_tracks} />

      {summary.scrobbles_window === 0 && (
        <div className={styles.section}>
          <div className={styles.eyebrow}>Sin escuchas recientes</div>
          <div className={styles.recentSub}>
            No hay listens en los últimos {summary.window_days} días. Tus tops
            aparecerán en cuanto vuelvas a escuchar música.
          </div>
        </div>
      )}

      {modalOpen && (
        <ContextDownloadModal
          slug="music"
          mcpPreview={mcpPreview()}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}

function SyncingView({ onReload }: { onReload: () => void }) {
  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>
      <Header />
      <div className={styles.soon}>
        <div className={styles.soonTitle}>Sincronizando tus escuchas…</div>
        <p className={styles.soonNote}>
          Estamos trayendo tus listens de ListenBrainz. Esto tarda unos segundos;
          actualiza para ver tu resumen.
        </p>
        <div style={{ marginTop: "20px", display: "flex", gap: "10px", justifyContent: "center" }}>
          <button type="button" className={styles.btnPrimary} onClick={onReload}>
            Actualizar
          </button>
        </div>
      </div>
    </div>
  );
}

function ConnectView({
  onConnected,
  detail,
  hadError,
}: {
  onConnected: () => void;
  detail: string | null;
  hadError: boolean;
}) {
  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>
      <Header />
      <div className={styles.soon}>
        <div className={styles.soonTitle}>Conecta tu música</div>
        <p className={styles.soonNote}>
          {hadError
            ? (detail ??
              "El último intento de sincronizar falló. Revisa tu usuario y vuelve a conectar.")
            : "Escribe tu nombre de usuario público de ListenBrainz para traer tus escuchas, artistas y canciones. No pedimos tu contraseña."}
        </p>
        <div style={{ marginTop: "20px" }}>
          <ConnectListenBrainzForm className={styles.btnPrimary} onConnected={onConnected} />
        </div>
      </div>
    </div>
  );
}

export function MusicDetail() {
  const { loading, source, error, reload } = useMusicSource();
  const [justConnected, setJustConnected] = useState(false);

  if (loading && !justConnected) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <p className={styles.headerBlurb}>Cargando tu música…</p>
      </div>
    );
  }

  if (!justConnected && (error || !source)) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <p className={styles.headerBlurb}>
          No se pudo cargar tu música. Inténtalo de nuevo más tarde.
        </p>
      </div>
    );
  }

  const state = source?.state;
  const isLive = state === "fresh" || state === "syncing";
  if (isLive && source?.summary) {
    return <ConnectedView source={source} summary={source.summary} onRefresh={reload} />;
  }
  if (state === "syncing" || justConnected) {
    return (
      <SyncingView
        onReload={() => {
          setJustConnected(false);
          reload();
        }}
      />
    );
  }
  return (
    <ConnectView
      detail={source?.detail ?? null}
      hadError={state === "error"}
      onConnected={() => {
        setJustConnected(true);
        reload();
      }}
    />
  );
}
