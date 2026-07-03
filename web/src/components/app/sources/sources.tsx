import Link from "next/link";
import type { CSSProperties } from "react";
import { CATEGORY_DETAIL, type CategoryDetailData } from "../category/data";
import styles from "./sources.module.css";

const HEALTH_CLASS: Record<"ok" | "warn" | "error", string> = {
  ok: styles.healthOk,
  warn: styles.healthWarn,
  error: styles.healthError,
};

function accentVar(accent: string): CSSProperties {
  return { "--catAccent": accent } as CSSProperties;
}

function LiveCard({ category }: { category: CategoryDetailData }) {
  return (
    <Link
      href={`/app/categoria/${category.slug}`}
      className={styles.card}
      style={accentVar(category.accent)}
    >
      <span className={styles.cardIcon}>{category.name.charAt(0)}</span>
      <div className={styles.cardBody}>
        <div className={styles.cardTitleRow}>
          <span className={styles.cardName}>{category.name}</span>
          {category.health && (
            <span
              className={`${styles.healthDot} ${HEALTH_CLASS[category.health.state]}`}
            />
          )}
        </div>
        <div className={styles.cardMeta}>
          {category.provider} · {category.modeLabel} · {category.freshLabel}
        </div>
      </div>
      <span className={styles.cardCta}>Abrir →</span>
    </Link>
  );
}

function SoonCard({ category }: { category: CategoryDetailData }) {
  return (
    <Link
      href={`/app/categoria/${category.slug}`}
      className={`${styles.card} ${styles.cardSoon}`}
    >
      <span className={styles.cardSoonHatch} aria-hidden="true" />
      <span className={`${styles.cardIcon} ${styles.cardIconSoon}`}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 8v4l3 2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <div className={`${styles.cardBody} ${styles.cardBodySoon}`}>
        <div className={styles.cardTitleRow}>
          <span className={`${styles.cardName} ${styles.cardNameSoon}`}>
            {category.name}
          </span>
          <span className={styles.soonDot} />
        </div>
        <div className={styles.cardMeta}>
          {category.provider} · {category.soonEta}
        </div>
      </div>
      <span className={styles.soonChip}>Próximamente</span>
    </Link>
  );
}

export function Sources() {
  const all = Object.values(CATEGORY_DETAIL);
  const live = all.filter((c) => c.state === "live");
  const soon = all.filter((c) => c.state === "soon");
  // v1: ninguna categoría "apagada" (existe sin datos); llegará con más fuentes.
  const off: CategoryDetailData[] = [];

  const summary = [
    { value: String(live.length), label: "activas" },
    { value: String(live.length), label: "expuestas por MCP" },
    { value: String(off.length), label: "apagadas" },
    { value: String(soon.length), label: "en desarrollo" },
  ];

  return (
    <div className="eth-screen">
      <p className={styles.intro}>
        Cada categoría es una <strong>fuente de contexto</strong> para tu IA.
        Conéctala por <strong>API</strong> o súbela por <strong>import</strong>;
        luego descarga su contexto o exponlo en vivo por <strong>MCP</strong>.
      </p>

      <div className={styles.summary}>
        {summary.map((item) => (
          <div key={item.label} className={styles.summaryCard}>
            <div className={styles.summaryValue}>{item.value}</div>
            <div className={styles.summaryLabel}>{item.label}</div>
          </div>
        ))}
      </div>

      <div className={styles.groupHead}>
        <span className={styles.groupDotLive} />
        <div className={styles.groupTitle}>Activas</div>
        <div className={styles.groupLine} />
        <span className={styles.groupCount}>{live.length}</span>
      </div>
      <div className={styles.grid}>
        {live.map((category) => (
          <LiveCard key={category.slug} category={category} />
        ))}
      </div>

      {soon.length > 0 && (
        <>
          <div className={`${styles.groupHead} ${styles.groupHeadSpaced}`}>
            <span className={styles.groupDotSoon} />
            <div className={styles.groupTitle}>En desarrollo · próximamente</div>
            <div className={styles.groupLine} />
            <span className={styles.groupCount}>{soon.length}</span>
          </div>
          <p className={styles.groupNote}>
            Estamos construyendo estos conectores. Todavía no se pueden activar,
            pero llegarán pronto.
          </p>
          <div className={styles.grid}>
            {soon.map((category) => (
              <SoonCard key={category.slug} category={category} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
