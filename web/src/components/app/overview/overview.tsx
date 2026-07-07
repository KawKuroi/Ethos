"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import type { GamesSummary } from "@/lib/api";
import { fmtInt } from "@/lib/format";
import { useActiveSources, type ActiveSourceView } from "@/lib/use-active-sources";
import { LoadingState } from "../loading-state";
import { GLOBAL_ALERTS, type GlobalAlert, MCP_CONNECTED } from "./data";
import styles from "./overview.module.css";

const ALERT_COLOR: Record<GlobalAlert["level"], string> = {
  warn: "var(--warn)",
  error: "var(--error)",
};

function accentVar(accent: string): CSSProperties {
  return { "--rowAccent": accent } as CSSProperties;
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

function StatBand({ summary, meta }: { summary: GamesSummary | null; meta: string }) {
  const stats = [
    { value: summary ? fmtInt(summary.games) : "—", label: "juegos" },
    { value: summary ? fmtInt(summary.hours) : "—", label: "horas" },
    { value: summary ? fmtInt(summary.wishlisted) : "—", label: "deseados" },
    {
      value:
        summary && summary.avg_completion_pct != null
          ? `${Math.round(summary.avg_completion_pct)}%`
          : "—",
      label: "completado",
    },
  ];

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

// Fila del panorama para cualquier categoría activable: activa muestra su
// métrica hero y barra; apagada invita a conectarla.
function SourceRow({ view, maxHero }: { view: ActiveSourceView; maxHero: number }) {
  const barPct =
    view.live && maxHero > 0
      ? Math.max(6, Math.round((view.heroValue / maxHero) * 100))
      : 0;

  return (
    <Link
      href={`/app/categoria/${view.slug}`}
      className={styles.row}
      style={accentVar(view.accent)}
    >
      <span className={`${styles.rowChip} ${view.live ? styles.rowChipLive : styles.rowChipSoon}`}>
        {view.initial}
      </span>
      <div className={styles.rowName}>
        <div className={`${styles.rowNameText} ${view.live ? styles.rowNameLive : styles.rowNameSoon}`}>
          {view.name}
        </div>
        <div className={styles.rowProvider}>
          {view.provider} · {view.modeLabel}
        </div>
      </div>

      {view.live ? (
        <>
          <div className={styles.bar}>
            <div className={styles.barFill} style={{ width: `${barPct}%` }} />
          </div>
          <div className={styles.rowValue}>
            {view.syncing ? (
              <span className={styles.rowHeroLabel}>sincronizando…</span>
            ) : (
              <>
                <span className={styles.rowHero}>{fmtInt(view.heroValue)}</span>
                <span className={styles.rowHeroLabel}>{view.heroLabel}</span>
              </>
            )}
          </div>
          <span className={styles.dotLive} aria-label="activa" />
        </>
      ) : view.soon ? (
        <>
          <div className={styles.barEmpty} />
          <span className={styles.offLabel}>en desarrollo →</span>
          <span className={styles.dotOff} aria-label="en desarrollo" />
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

function Panorama({ views }: { views: ActiveSourceView[] }) {
  // La barra de cada fila es relativa al hero mayor entre las activas. Las
  // métricas mezclan unidades (horas, escuchas…), pero la barra solo dibuja
  // proporción visual, como en el prototipo.
  const maxHero = Math.max(0, ...views.filter((v) => v.live).map((v) => v.heroValue));
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
            apagada
          </span>
        </div>
      </div>
      <div className={`${styles.card} ${styles.panorama}`}>
        {views.map((view) => (
          <SourceRow key={view.slug} view={view} maxHero={maxHero} />
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
            <div key={game.title} className={styles.event} style={accentVar("#3b82c4")}>
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

function activeMeta(views: ActiveSourceView[]): string {
  const providers = views.filter((v) => v.live).map((v) => v.provider);
  if (providers.length === 0) return "Sin fuentes activas";
  const label = providers.length === 1 ? "fuente activa" : "fuentes activas";
  return `${providers.length} ${label} · ${providers.join(" · ")}`;
}

export function Overview() {
  const { loading, views, gamesSummary } = useActiveSources();

  return (
    <div className="eth-screen">
      {!MCP_CONNECTED && <McpBanner />}
      <GlobalAlerts />
      {loading ? (
        <LoadingState label="Cargando tu perfil…" />
      ) : (
        <>
          <StatBand summary={gamesSummary} meta={activeMeta(views)} />
          <Panorama views={views} />
          <Activity summary={gamesSummary} />
        </>
      )}
    </div>
  );
}
