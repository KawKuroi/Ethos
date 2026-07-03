import Link from "next/link";
import type { CSSProperties } from "react";
import {
  ACTIVITY,
  GLOBAL_ALERTS,
  type GlobalAlert,
  MCP_CONNECTED,
  OV_META,
  OV_STATS,
  PANORAMA,
  type PanoramaRow,
} from "./data";
import styles from "./overview.module.css";

const ALERT_COLOR: Record<GlobalAlert["level"], string> = {
  warn: "var(--warn)",
  error: "var(--error)",
};

// Fija el acento de la fila/evento como variable CSS local.
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

function StatBand() {
  return (
    <div className={`${styles.card} ${styles.statBand}`}>
      <div className={styles.statHead}>
        <div className={styles.eyebrow}>El gusto en números</div>
        <div className={styles.statMeta}>{OV_META}</div>
      </div>
      <div className={styles.statGrid}>
        {OV_STATS.map((stat) => (
          <div key={stat.label} className={styles.statCell}>
            <div className={styles.statValue}>{stat.value}</div>
            <div className={styles.statLabel}>{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PanoramaRowView({ row }: { row: PanoramaRow }) {
  const live = row.state === "live";
  return (
    <Link
      href={`/app/categoria/${row.id}`}
      className={styles.row}
      style={accentVar(row.accent)}
    >
      <span
        className={`${styles.rowChip} ${live ? styles.rowChipLive : styles.rowChipSoon}`}
      >
        {row.initial}
      </span>
      <div className={styles.rowName}>
        <div
          className={`${styles.rowNameText} ${live ? styles.rowNameLive : styles.rowNameSoon}`}
        >
          {row.name}
        </div>
        <div className={styles.rowProvider}>
          {row.provider} · {row.modeLabel}
        </div>
      </div>

      {live ? (
        <>
          <div className={styles.bar}>
            <div className={styles.barFill} style={{ width: `${row.barPct}%` }} />
          </div>
          <div className={styles.rowValue}>
            <span className={styles.rowHero}>{row.heroValue}</span>
            <span className={styles.rowHeroLabel}>{row.heroLabel}</span>
          </div>
          <span className={styles.dotLive} aria-label="activa" />
        </>
      ) : (
        <>
          <div className={styles.barEmpty} />
          <span className={styles.soonLabel}>en desarrollo · próximamente</span>
          <span className={styles.dotSoon} aria-label="en desarrollo" />
        </>
      )}
    </Link>
  );
}

function Panorama() {
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
        {PANORAMA.map((row) => (
          <PanoramaRowView key={row.id} row={row} />
        ))}
      </div>
    </>
  );
}

function Activity() {
  return (
    <div className={`${styles.card} ${styles.activity}`}>
      <div className={styles.activityTitle}>Actividad reciente</div>
      <div className={styles.activitySub}>
        Últimas sincronizaciones desde tus fuentes conectadas.
      </div>
      <div className={styles.timeline}>
        <span className={styles.timelineLine} aria-hidden="true" />
        {ACTIVITY.map((item) => (
          <div key={item.id} className={styles.event} style={accentVar(item.accent)}>
            <span className={styles.eventPin} aria-hidden="true" />
            <div className={styles.eventText}>{item.text}</div>
            <div className={styles.eventMeta}>
              <span className={styles.eventCat}>{item.catName}</span> · {item.time}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function Overview() {
  return (
    <div className="eth-screen">
      {!MCP_CONNECTED && <McpBanner />}
      <GlobalAlerts />
      <StatBand />
      <Panorama />
      <Activity />
    </div>
  );
}
