"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import type { GamesSource, GamesSummary } from "@/lib/api";
import { useGamesSource } from "@/lib/use-games-source";
import {
  GLOBAL_ALERTS,
  type GlobalAlert,
  MCP_CONNECTED,
  PANORAMA,
  type PanoramaRow,
} from "./data";
import styles from "./overview.module.css";

const ALERT_COLOR: Record<GlobalAlert["level"], string> = {
  warn: "var(--warn)",
  error: "var(--error)",
};

const GAMES = PANORAMA.find((r) => r.id === "games") as PanoramaRow;
const SOON = PANORAMA.filter((r) => r.state === "soon");

function accentVar(accent: string): CSSProperties {
  return { "--rowAccent": accent } as CSSProperties;
}

function fmt(n: number): string {
  return Math.round(n).toLocaleString("es-ES");
}

function McpBanner() {
  return (
    <div className={styles.banner}>
      <span className={styles.bannerDot} aria-hidden="true" />
      <div className={styles.bannerBody}>
        <div className={styles.bannerTitle}>Tu IA aún no está conectada</div>
        <div className={styles.bannerSub}>
          El perfil está listo y normalizado, esperando a que lo consultes.
        </div>
      </div>
      <Link href="/app/conectar-ia" className={styles.bannerBtn}>
        Conectar IA →
      </Link>
    </div>
  );
}

function GlobalAlerts() {
  if (GLOBAL_ALERTS.length === 0) return null;
  const errors = GLOBAL_ALERTS.filter((a) => a.level === "error").length;
  const warns = GLOBAL_ALERTS.length - errors;
  const parts: string[] = [];
  if (errors > 0) parts.push(`${errors} con error`);
  if (warns > 0) parts.push(`${warns} por revisar`);

  return (
    <div className={`${styles.card} ${styles.alerts}`}>
      <div className={styles.alertsHead}>
        <span className={styles.alertsIcon} aria-hidden="true">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 3.5 22 20H2L12 3.5Z" strokeLinejoin="round" />
            <path d="M12 10v4" strokeLinecap="round" />
            <circle cx="12" cy="17" r=".6" fill="currentColor" stroke="none" />
          </svg>
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className={styles.alertsTitle}>Necesitan tu atención</div>
          <div className={styles.alertsCount}>{parts.join(" · ")}</div>
        </div>
      </div>
      {GLOBAL_ALERTS.map((alert) => (
        <div
          key={alert.id}
          className={styles.alertRow}
          style={{ "--alertColor": ALERT_COLOR[alert.level] } as CSSProperties}
        >
          <span className={styles.alertDot} aria-hidden="true" />
          <span className={styles.alertLevel}>{alert.level}</span>
          <div className={styles.alertText}>
            <strong style={{ fontWeight: 600 }}>{alert.catName}</strong> ·{" "}
            {alert.text}
          </div>
          <span className={styles.alertTime}>{alert.time}</span>
          {alert.action && (
            <button type="button" className={styles.alertAction}>
              {alert.action}
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

function StatBand({ summary }: { summary: GamesSummary | null }) {
  const stats = [
    { value: summary ? fmt(summary.games) : "—", label: "juegos" },
    { value: summary ? fmt(summary.hours) : "—", label: "horas" },
    { value: summary ? fmt(summary.wishlisted) : "—", label: "deseados" },
    {
      value:
        summary && summary.avg_completion_pct != null
          ? `${Math.round(summary.avg_completion_pct)}%`
          : "—",
      label: "completado",
    },
  ];
  const meta = summary ? "1 fuente activa · Steam" : "Sin fuentes activas";

  return (
    <div className={`${styles.card} ${styles.statBand}`}>
      <div className={styles.statHead}>
        <div className={styles.eyebrow}>El gusto en números</div>
        <div className={styles.statMeta}>{meta}</div>
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
  );
}

type RowVariant = "live" | "soon" | "off";

function GamesRow({ source }: { source: GamesSource | null }) {
  const state = source?.state;
  const variant: RowVariant =
    state === "fresh" || state === "syncing" ? "live" : "off";
  const hours = source?.summary?.hours ?? 0;
  const syncing = state === "syncing";

  return (
    <Link
      href={`/app/categoria/${GAMES.id}`}
      className={styles.row}
      style={accentVar(GAMES.accent)}
    >
      <span className={`${styles.rowChip} ${variant === "live" ? styles.rowChipLive : styles.rowChipSoon}`}>
        {GAMES.initial}
      </span>
      <div className={styles.rowName}>
        <div className={`${styles.rowNameText} ${variant === "live" ? styles.rowNameLive : styles.rowNameSoon}`}>
          {GAMES.name}
        </div>
        <div className={styles.rowProvider}>
          {GAMES.provider} · {GAMES.modeLabel}
        </div>
      </div>

      {variant === "live" ? (
        <>
          <div className={styles.bar}>
            <div className={styles.barFill} style={{ width: "100%" }} />
          </div>
          <div className={styles.rowValue}>
            {syncing ? (
              <span className={styles.rowHeroLabel}>sincronizando…</span>
            ) : (
              <>
                <span className={styles.rowHero}>{fmt(hours)}</span>
                <span className={styles.rowHeroLabel}>horas jugadas</span>
              </>
            )}
          </div>
          <span className={styles.dotLive} aria-label="activa" />
        </>
      ) : (
        <>
          <div className={styles.barEmpty} />
          <span className={styles.offLabel}>conéctala →</span>
          <span className={styles.dotOff} aria-label="apagada" />
        </>
      )}
    </Link>
  );
}

function SoonRow({ row }: { row: PanoramaRow }) {
  return (
    <Link href={`/app/categoria/${row.id}`} className={styles.row} style={accentVar(row.accent)}>
      <span className={`${styles.rowChip} ${styles.rowChipSoon}`}>{row.initial}</span>
      <div className={styles.rowName}>
        <div className={`${styles.rowNameText} ${styles.rowNameSoon}`}>{row.name}</div>
        <div className={styles.rowProvider}>
          {row.provider} · {row.modeLabel}
        </div>
      </div>
      <div className={styles.barEmpty} />
      <span className={styles.soonLabel}>en desarrollo · próximamente</span>
      <span className={styles.dotSoon} aria-label="en desarrollo" />
    </Link>
  );
}

function Panorama({ source }: { source: GamesSource | null }) {
  return (
    <>
      <div className={styles.panoHead}>
        <div className={styles.eyebrow}>Panorama · por actividad</div>
        <div className={styles.legend}>
          <span className={styles.legendItem}>
            <span className={styles.legendDotLive} />
            activa
          </span>
          <span className={styles.legendItem}>
            <span className={styles.legendDotSoon} />
            en desarrollo
          </span>
        </div>
      </div>
      <div className={`${styles.card} ${styles.panorama}`}>
        <GamesRow source={source} />
        {SOON.map((row) => (
          <SoonRow key={row.id} row={row} />
        ))}
      </div>
    </>
  );
}

function Activity({ summary }: { summary: GamesSummary | null }) {
  const events = summary?.recently_played ?? [];
  return (
    <div className={`${styles.card} ${styles.activity}`}>
      <div className={styles.activityTitle}>Actividad reciente</div>
      <div className={styles.activitySub}>
        Últimas sincronizaciones desde tus fuentes conectadas.
      </div>
      {events.length === 0 ? (
        <div className={styles.activitySub}>
          Aún no hay actividad. Conecta una fuente para verla aquí.
        </div>
      ) : (
        <div className={styles.timeline}>
          <span className={styles.timelineLine} aria-hidden="true" />
          {events.map((game) => (
            <div key={game.title} className={styles.event} style={accentVar(GAMES.accent)}>
              <span className={styles.eventPin} aria-hidden="true" />
              <div className={styles.eventText}>Jugaste a {game.title}</div>
              <div className={styles.eventMeta}>
                <span className={styles.eventCat}>Juegos</span> · +{game.hours_2weeks} h
                · 2 sem
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function Overview() {
  const { loading, source } = useGamesSource();
  const summary = source?.summary ?? null;

  return (
    <div className="eth-screen">
      {!MCP_CONNECTED && <McpBanner />}
      <GlobalAlerts />
      {loading ? (
        <div className={styles.loading}>Cargando tu perfil…</div>
      ) : (
        <>
          <StatBand summary={summary} />
          <Panorama source={source} />
          <Activity summary={summary} />
        </>
      )}
    </div>
  );
}
