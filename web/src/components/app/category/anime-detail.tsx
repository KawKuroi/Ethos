"use client";

import { useState } from "react";
import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import {
  connectAniList,
  refreshAniList,
  type AnimeSource,
  type AnimeSummary,
} from "@/lib/api";
import { fmtInt, relativeTime } from "@/lib/format";
import { useAnimeSource } from "@/lib/use-anime-source";
import { ConnectUsernameForm } from "../connect-username";
import { ContextDownloadModal } from "./context-modal";
import { CATEGORY_DETAIL } from "./data";
import styles from "./category.module.css";

const ANIME = CATEGORY_DETAIL.anime;

function accentVar(): CSSProperties {
  return { "--catAccent": ANIME.accent } as CSSProperties;
}

function mcpPreview(): string {
  return [
    "// Tu IA descubre y llama la herramienta",
    'ethos.context({ tool: "anime.*", ask: "mis mejor puntuados" })',
    "",
    "→ 200 OK · contexto acotado servido en vivo",
    "  { provider, summary, top_rated, current }",
  ].join("\n");
}

function mediaLabel(mediaType: string): string {
  return mediaType === "manga" ? "Manga" : "Anime";
}

function Header({ actions }: { actions?: ReactNode }) {
  return (
    <div className={styles.header}>
      <span className={styles.headerIcon}>A</span>
      <div className={styles.headerBody}>
        <h2 className={styles.headerName}>Anime y manga</h2>
        <div className={styles.headerBlurb}>{ANIME.blurb}</div>
      </div>
      {actions && <div className={styles.headerActions}>{actions}</div>}
    </div>
  );
}

function TopRated({ summary }: { summary: AnimeSummary }) {
  if (summary.top_rated.length === 0) return null;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Mejor puntuados · tu nota</div>
      {summary.top_rated.map((entry, i) => (
        <div key={`${entry.media_type}-${entry.title}`} className={styles.topRow}>
          <div className={styles.rank}>{i + 1}</div>
          <div className={styles.topBody}>
            <div className={styles.topHead}>
              <span className={styles.topName}>{entry.title}</span>
              <span className={styles.topValue}>{entry.score}/100</span>
            </div>
            <div className={styles.topSub}>{mediaLabel(entry.media_type)}</div>
            <div className={styles.topBar}>
              <div className={styles.topBarFill} style={{ width: `${entry.score}%` }} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function Current({ summary }: { summary: AnimeSummary }) {
  if (summary.current.length === 0) return null;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>En curso</div>
      {summary.current.map((entry) => (
        <div key={`${entry.media_type}-${entry.title}`} className={styles.recentRow}>
          <span className={styles.recentDot} />
          <div className={styles.recentBody}>
            <div className={styles.recentName}>{entry.title}</div>
            <div className={styles.recentSub}>{mediaLabel(entry.media_type)}</div>
          </div>
          <span className={styles.recentTime}>
            {entry.progress} {entry.media_type === "manga" ? "cap" : "ep"}
          </span>
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
  source: AnimeSource;
  summary: AnimeSummary;
  onRefresh: () => void;
}) {
  const [refreshing, setRefreshing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  async function refresh() {
    if (refreshing) return;
    setRefreshing(true);
    try {
      await refreshAniList();
    } finally {
      setRefreshing(false);
      onRefresh();
    }
  }

  const stats = [
    { value: fmtInt(summary.anime_watched), label: "animes vistos" },
    { value: fmtInt(summary.manga_read), label: "mangas leídos" },
    { value: fmtInt(summary.chapters_read), label: "capítulos" },
    {
      value: summary.mean_score != null ? `${Math.round(summary.mean_score)}` : "—",
      label: "nota media",
    },
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
          Proveedor <span className={styles.provider}>AniList</span>
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
            <div className={styles.heroValue}>{fmtInt(summary.episodes_watched)}</div>
            <div className={styles.heroLabel}>episodios vistos</div>
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

      <TopRated summary={summary} />
      <Current summary={summary} />

      {modalOpen && (
        <ContextDownloadModal
          slug="anime"
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
        <div className={styles.soonTitle}>Sincronizando tus listas…</div>
        <p className={styles.soonNote}>
          Estamos trayendo tus animes y mangas de AniList. Esto tarda unos
          segundos; actualiza para ver tu resumen.
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
  hadProblem,
}: {
  onConnected: () => void;
  detail: string | null;
  hadProblem: boolean;
}) {
  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>
      <Header />
      <div className={styles.soon}>
        <div className={styles.soonTitle}>Conecta tu anime y manga</div>
        <p className={styles.soonNote}>
          {hadProblem
            ? (detail ??
              "El último intento de sincronizar falló. Revisa tu usuario y vuelve a conectar.")
            : "Escribe tu nombre de usuario de AniList para traer tus listas de anime y manga. No pedimos tu contraseña; tus listas deben ser públicas."}
        </p>
        <div style={{ marginTop: "20px" }}>
          <ConnectUsernameForm
            className={styles.btnPrimary}
            placeholder="Tu usuario de AniList"
            ariaLabel="Nombre de usuario de AniList"
            errorText="No se pudo conectar. Revisa tu nombre de usuario de AniList e inténtalo de nuevo."
            connect={connectAniList}
            onConnected={onConnected}
          />
        </div>
      </div>
    </div>
  );
}

export function AnimeDetail() {
  const { loading, source, error, reload } = useAnimeSource();
  const [justConnected, setJustConnected] = useState(false);

  if (loading && !justConnected) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <p className={styles.headerBlurb}>Cargando tu anime y manga…</p>
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
          No se pudo cargar tu anime y manga. Inténtalo de nuevo más tarde.
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
      hadProblem={state === "error" || state === "private"}
      onConnected={() => {
        setJustConnected(true);
        reload();
      }}
    />
  );
}
