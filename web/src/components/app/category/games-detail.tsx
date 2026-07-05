"use client";

import { useState } from "react";
import Link from "next/link";
import type { CSSProperties } from "react";
import { refreshSteam, type GamesSource, type GamesSummary } from "@/lib/api";
import { relativeTime } from "@/lib/format";
import { useGamesSource } from "@/lib/use-games-source";
import { ConnectSteamButton } from "../connect-steam";
import { ContextDownloadModal } from "./context-modal";
import { CATEGORY_DETAIL } from "./data";
import styles from "./category.module.css";

const GAMES = CATEGORY_DETAIL.games;

function accentVar(): CSSProperties {
  return { "--catAccent": GAMES.accent } as CSSProperties;
}

function mcpPreview(): string {
  return [
    "// Tu IA descubre y llama la herramienta",
    'ethos.context({ tool: "games.*", ask: "resumen reciente" })',
    "",
    "→ 200 OK · contexto acotado servido en vivo",
    "  { provider, summary, top_by_hours, recently_played, wishlist }",
  ].join("\n");
}

function ConnectedView({
  source,
  summary,
  onRefresh,
}: {
  source: GamesSource;
  summary: GamesSummary;
  onRefresh: () => void;
}) {
  const [refreshing, setRefreshing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const maxHours = summary.top_by_hours[0]?.hours || 1;

  async function refresh() {
    if (refreshing) return;
    setRefreshing(true);
    try {
      await refreshSteam();
    } finally {
      setRefreshing(false);
      onRefresh();
    }
  }

  const stats = [
    { value: summary.games.toLocaleString("es-ES"), label: "juegos" },
    { value: Math.round(summary.hours).toLocaleString("es-ES"), label: "horas" },
    { value: summary.wishlisted.toLocaleString("es-ES"), label: "deseados" },
    {
      value:
        summary.avg_completion_pct != null
          ? `${Math.round(summary.avg_completion_pct)}%`
          : "—",
      label: "completado",
    },
  ];

  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>

      <div className={styles.header}>
        <span className={styles.headerIcon}>J</span>
        <div className={styles.headerBody}>
          <h2 className={styles.headerName}>Juegos</h2>
          <div className={styles.headerBlurb}>{GAMES.blurb}</div>
        </div>
        <div className={styles.headerActions}>
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
        </div>
      </div>

      <div className={styles.strip}>
        <span className={styles.stripItem}>
          <span className={`${styles.healthDot} ${styles.healthOk}`} />
          <span className={styles.stripStrong}>Operativa</span>
        </span>
        <span className={styles.stripSep} />
        <span className={styles.stripItem}>
          Proveedor <span className={styles.provider}>Steam</span>
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
            <div className={styles.heroValue}>
              {Math.round(summary.hours).toLocaleString("es-ES")}
            </div>
            <div className={styles.heroLabel}>horas jugadas</div>
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

      {summary.top_by_hours.length > 0 && (
        <div className={styles.section}>
          <div className={styles.eyebrow}>Top por horas</div>
          {summary.top_by_hours.map((game, i) => (
            <div key={game.title} className={styles.topRow}>
              <div className={styles.rank}>{i + 1}</div>
              <div className={styles.topBody}>
                <div className={styles.topHead}>
                  <span className={styles.topName}>{game.title}</span>
                  <span className={styles.topValue}>{Math.round(game.hours)} h</span>
                </div>
                <div className={styles.topSub}>
                  {game.completion_pct != null
                    ? `${Math.round(game.completion_pct)}% completado`
                    : "—"}
                </div>
                <div className={styles.topBar}>
                  <div
                    className={styles.topBarFill}
                    style={{ width: `${Math.round((game.hours / maxHours) * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {summary.recently_played.length > 0 && (
        <div className={styles.section}>
          <div className={styles.eyebrow}>Jugado recientemente</div>
          {summary.recently_played.map((game) => (
            <div key={game.title} className={styles.recentRow}>
              <span className={styles.recentDot} />
              <div className={styles.recentBody}>
                <div className={styles.recentName}>{game.title}</div>
                <div className={styles.recentSub}>+{game.hours_2weeks} h · 2 sem</div>
              </div>
              <span className={styles.recentTime}>reciente</span>
            </div>
          ))}
        </div>
      )}

      {summary.wishlisted > 0 && (
        <div className={styles.section}>
          <div className={styles.eyebrow}>Deseados</div>
          <div className={styles.recentSub}>
            {summary.wishlisted.toLocaleString("es-ES")} juegos en tu lista de deseados.
            Los títulos llegan pronto.
          </div>
        </div>
      )}

      {modalOpen && (
        <ContextDownloadModal
          slug="games"
          mcpPreview={mcpPreview()}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}

function OffView({ state, detail }: { state: GamesSource["state"]; detail: string | null }) {
  const isPrivate = state === "private";
  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>
      <div className={styles.header}>
        <span className={styles.headerIcon}>J</span>
        <div className={styles.headerBody}>
          <h2 className={styles.headerName}>Juegos</h2>
          <div className={styles.headerBlurb}>{GAMES.blurb}</div>
        </div>
      </div>
      <div className={styles.soon}>
        <div className={styles.soonTitle}>
          {isPrivate ? "Tu perfil de Steam es privado" : "Esta categoría está apagada"}
        </div>
        <p className={styles.soonNote}>
          {isPrivate
            ? (detail ??
              "Pon tu perfil y tus datos de juego en público en Steam, y vuelve a refrescar.")
            : "Conecta tu cuenta de Steam por OpenID para traer tu biblioteca, horas y deseados. No pedimos tu contraseña."}
        </p>
        <div style={{ marginTop: "20px", display: "flex", gap: "10px", justifyContent: "center" }}>
          <ConnectSteamButton className={styles.btnPrimary} />
        </div>
      </div>
    </div>
  );
}

export function GamesDetail() {
  const { loading, source, error } = useGamesSource();

  if (loading) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <p className={styles.headerBlurb}>Cargando tu biblioteca…</p>
      </div>
    );
  }

  if (error || !source) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <p className={styles.headerBlurb}>
          No se pudo cargar tu biblioteca. Inténtalo de nuevo más tarde.
        </p>
      </div>
    );
  }

  const isLive = source.state === "fresh" || source.state === "syncing";
  if (isLive && source.summary) {
    return <ConnectedView source={source} summary={source.summary} onRefresh={() => location.reload()} />;
  }
  return <OffView state={source.state} detail={source.detail} />;
}
