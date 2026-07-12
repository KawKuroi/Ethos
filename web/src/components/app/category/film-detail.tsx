"use client";

import { useState } from "react";
import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import {
  refreshSource,
  type FilmSource,
  type FilmSummary,
} from "@/lib/api";
import { fmtInt, relativeTime } from "@/lib/format";
import { useAutoReload } from "@/lib/use-source";
import { useFilmSource } from "@/lib/use-film-source";
import { ConnectHub } from "../connect-hub";
import { LoadingState } from "../loading-state";
import { ContextDownloadModal } from "./context-modal";
import { CATEGORY_DETAIL } from "./data";
import { ManualEntries } from "./manual-entries";
import { providerName } from "./providers";
import styles from "./category.module.css";

const FILM = CATEGORY_DETAIL.film;

function accentVar(): CSSProperties {
  return { "--catAccent": FILM.accent } as CSSProperties;
}

function mcpPreview(): string {
  return [
    "// Tu IA descubre y llama la herramienta",
    'ethos.context({ tool: "film_*", ask: "más vistas este año" })',
    "",
    "→ 200 OK · contexto acotado servido en vivo",
    "  { provider, summary, top_movies, top_shows, recently_watched }",
  ].join("\n");
}

function Header({ actions }: { actions?: ReactNode }) {
  return (
    <div className={styles.header}>
      <span className={styles.headerIcon}>C</span>
      <div className={styles.headerBody}>
        <h2 className={styles.headerName}>Cine y TV</h2>
        <div className={styles.headerBlurb}>{FILM.blurb}</div>
      </div>
      {actions && <div className={styles.headerActions}>{actions}</div>}
    </div>
  );
}

function TopMovies({ summary }: { summary: FilmSummary }) {
  if (summary.top_movies.length === 0) return null;
  const max = summary.top_movies[0]?.plays || 1;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Top películas · por reproducciones</div>
      {summary.top_movies.map((movie, i) => (
        <div key={`${movie.title}-${movie.year}`} className={styles.topRow}>
          <div className={styles.rank}>{i + 1}</div>
          <div className={styles.topBody}>
            <div className={styles.topHead}>
              <span className={styles.topName}>{movie.title}</span>
              <span className={styles.topValue}>
                {movie.plays} {movie.plays === 1 ? "vez" : "veces"}
              </span>
            </div>
            {movie.year != null && <div className={styles.topSub}>{movie.year}</div>}
            <div className={styles.topBar}>
              <div
                className={styles.topBarFill}
                style={{ width: `${Math.round((movie.plays / max) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function TopShows({ summary }: { summary: FilmSummary }) {
  if (summary.top_shows.length === 0) return null;
  const max = summary.top_shows[0]?.episodes_watched || 1;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Top series · por episodios vistos</div>
      {summary.top_shows.map((show, i) => (
        <div key={show.title} className={styles.topRow}>
          <div className={styles.rank}>{i + 1}</div>
          <div className={styles.topBody}>
            <div className={styles.topHead}>
              <span className={styles.topName}>{show.title}</span>
              <span className={styles.topValue}>{show.episodes_watched} ep</span>
            </div>
            <div className={styles.topBar}>
              <div
                className={styles.topBarFill}
                style={{ width: `${Math.round((show.episodes_watched / max) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function RecentlyWatched({ summary }: { summary: FilmSummary }) {
  if (summary.recently_watched.length === 0) return null;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Visto recientemente</div>
      {summary.recently_watched.map((watch) => (
        <div key={`${watch.media_type}-${watch.title}`} className={styles.recentRow}>
          <span className={styles.recentDot} />
          <div className={styles.recentBody}>
            <div className={styles.recentName}>{watch.title}</div>
            <div className={styles.recentSub}>
              {watch.media_type === "movie" ? "Película" : "Serie"}
            </div>
          </div>
          <span className={styles.recentTime}>{relativeTime(watch.watched_at)}</span>
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
  source: FilmSource;
  summary: FilmSummary;
  onRefresh: () => void;
}) {
  const [refreshing, setRefreshing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [hubOpen, setHubOpen] = useState(false);
  const provider = source.provider ?? "trakt";
  const isImport = source.mode === "import";

  async function refresh() {
    if (refreshing) return;
    setRefreshing(true);
    try {
      await refreshSource(provider);
    } finally {
      setRefreshing(false);
      onRefresh();
    }
  }

  const stats = [
    { value: fmtInt(summary.movies_watched), label: "películas" },
    { value: fmtInt(summary.shows_watched), label: "series" },
    { value: fmtInt(summary.episodes_watched), label: "episodios" },
  ];

  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>

      <Header
        actions={
          <>
            {!isImport && (
              <button type="button" className={styles.btnGhost} onClick={refresh}>
                {refreshing ? <span className={styles.spin} /> : null}
                {refreshing ? "Sincronizando…" : "Refrescar"}
              </button>
            )}
            <button
              type="button"
              className={styles.btnGhost}
              onClick={() => setHubOpen((v) => !v)}
            >
              {isImport ? "Actualizar o cambiar fuente" : "Cambiar de fuente"}
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
          Proveedor{" "}
          <span className={styles.provider}>{providerName(provider) ?? "Trakt"}</span>
        </span>
        <span className={styles.stripItem}>
          Modo{" "}
          <span className={styles.stripStrong}>
            {isImport ? "Import · manual" : "API · en vivo"}
          </span>
        </span>
        <span className={styles.stripGrow} />
        <span className={styles.stripItem}>Actualizado {relativeTime(source.synced_at)}</span>
      </div>

      {hubOpen && (
        <div className={styles.section}>
          <div className={styles.eyebrow}>Tu fuente de cine y series</div>
          <ConnectHub
            slug="film"
            currentProvider={provider}
            className={styles.btnPrimary}
            onConnected={() => {
              setHubOpen(false);
              onRefresh();
            }}
          />
        </div>
      )}

      <div className={styles.statBand}>
        <div className={styles.statHero}>
          <div>
            <div className={styles.heroValue}>{fmtInt(summary.hours)}</div>
            <div className={styles.heroLabel}>horas vistas</div>
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

      <TopMovies summary={summary} />
      <TopShows summary={summary} />
      <RecentlyWatched summary={summary} />
      <ManualEntries slug="film" accent={FILM.accent} onChange={onRefresh} />

      {modalOpen && (
        <ContextDownloadModal
          slug="film"
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
        <div className={styles.soonTitle}>Sincronizando lo que has visto…</div>
        <p className={styles.soonNote}>
          Estamos trayendo tus películas y series de Trakt. Esto tarda unos
          segundos y la pantalla se actualizará sola.
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
  onChanged,
  detail,
  hadProblem,
}: {
  onConnected: () => void;
  onChanged: () => void;
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
        <div className={styles.soonTitle}>Conecta tu cine y series</div>
        <p className={styles.soonNote}>
          {hadProblem
            ? (detail ??
              "El último intento de sincronizar falló. Revisa tu fuente y vuelve a conectar.")
            : "Elige tu proveedor: Trakt por API con tu usuario público, o sube tu export de Letterboxd o IMDb. Nunca pedimos tu contraseña."}
        </p>
        <div style={{ marginTop: "20px" }}>
          <ConnectHub slug="film" className={styles.btnPrimary} onConnected={onConnected} />
        </div>
      </div>
      {/* Entradas a mano sin proveedor (D51): cuentan en el resumen y el
          refresco las conserva cuando conectes una fuente. */}
      <ManualEntries slug="film" accent={FILM.accent} onChange={onChanged} />
    </div>
  );
}

export function FilmDetail() {
  const { loading, source, error, reload, silentReload } = useFilmSource();
  const [justConnected, setJustConnected] = useState(false);
  // Mientras el refresco corre en segundo plano, la vista se actualiza sola;
  // para al llegar el resumen o un estado terminal (privado/error).
  const state = source?.state;
  const settled =
    (state === "fresh" && !!source?.summary) ||
    state === "private" ||
    state === "error";
  useAutoReload((justConnected || state === "syncing") && !settled, silentReload);

  if (loading && !justConnected) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <LoadingState label="Cargando tu cine y series…" />
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
          No se pudo cargar tu cine y series. Inténtalo de nuevo más tarde.
        </p>
      </div>
    );
  }

  const isLive = state === "fresh" || state === "syncing";
  // silentReload: el refresco sustituye los datos en sitio, sin volver a
  // pasar por la pantalla de carga (el botón ya muestra su propio spinner).
  if (isLive && source?.summary) {
    return <ConnectedView source={source} summary={source.summary} onRefresh={silentReload} />;
  }
  if (state === "syncing" || (justConnected && (!state || state === "never"))) {
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
      onChanged={silentReload}
      onConnected={() => {
        setJustConnected(true);
        reload();
      }}
    />
  );
}
